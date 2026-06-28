import os
import re
import time
from typing import List
from dotenv import load_dotenv

import pandas as pd
import psycopg2
from psycopg2 import sql

from src.spell_corrector import normalize_query, build_enriched_query
from src.llm_spell_corrector import create_llm_spell_corrector, create_llm_query_enhancer, combine_corrections

from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from operator import itemgetter

from pinecone.exceptions import PineconeApiException # <-- New addition

load_dotenv() # <-- Load environment variables from .env

# --- LLM Initialization ---
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# --- PostgreSQL Setup ---
db_params = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'dbname': os.getenv('DB_NAME'),
}

def execute_sql_query(query: str):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**db_params)
        print("Database connection successful!")
        cursor = conn.cursor()
        cursor.execute(query)

        column_names = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(column_names, row)))
        return results

    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@tool
def sql_query_tool(query: str) -> List[dict]:
    """Executes a SQL query on the PostgreSQL database and returns the result set.
    Input should be a well-formed SQL query string.
    """
    print("Executing SQL query with tool:", query)
    return execute_sql_query(query)

# --- LLM Chains for Classification and SQL Generation ---
input_classifier_prompt = PromptTemplate.from_template(
    """You are an expert in classifying customer queries for an airline support system.
Classify the following user query into one of these categories:
'Need SQL', 'Non SQL', or 'Out of Context'.

Guidelines for classification:
- 'Need SQL' is for queries that require fetching real-time flight data (flight schedules, availability, status, delays, bookings, fares)
- 'Non SQL' is for queries about airline policies, procedures, FAQs, or general information
- 'Out of Context' is for queries completely unrelated to airline support

Even if the query contains misspellings, typos, or grammatical errors, classify based on the intent.
Be lenient and assume the best interpretation of the user's intent.

Query: {query}

Classification:"""
)
input_classifier_chain = input_classifier_prompt | llm

sql_query_generation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a PostgreSQL expert for an airline system. Your task is to generate accurate SQL queries.

TABLE SCHEMA:
flights table with the following structure:\n    | Column Name    | Data Type | Description                                            |\n    | -------------- | --------- | ------------------------------------------------------ |\n    | id             | BIGINT    | Unique identifier for each flight record (Primary Key) |\n    | flight_no      | TEXT      | Flight number (e.g., AI695, SG528)                     |\n    | airline_code   | TEXT      | Airline code (e.g., AI, SG, IX)                        |\n    | airline_name   | TEXT      | Full airline name                                      |\n    | origin         | TEXT      | Origin airport code                                    |\n    | destination    | TEXT      | Destination airport code                               |\n    | departure_date | DATE      | Scheduled departure date                               |\n    | departure_time | TIME       | Scheduled departure time                               |\n    | arrival_date   | DATE      | Scheduled arrival date                                 |\n    | arrival_time | TIME      | Scheduled arrival time                                 |\n    | status         | TEXT      | Current flight status (On Time, Delayed, Cancelled)    |\n    | delay_minutes  | INTEGER   | Delay duration in minutes                              |\n    | delay_reason   | TEXT      | Reason for delay, if applicable                        |\n    | terminal       | TEXT      | Departure terminal                                     |\n    | gate           | TEXT      | Departure gate number                                  |\n    | aircraft_type  | TEXT      | Aircraft model used for the flight                     |\n    | seats_total    | INTEGER   | Total number of seats available                        |\n    | seats_booked   | INTEGER   | Number of seats already booked                         |\n    | fare_inr       | INTEGER   | Ticket fare in Indian Rupees                           |\n\n    Always include the `WHERE` clause if there are specific conditions mentioned in the user's question.\n    Ensure the queries are read-only and do not contain any `UPDATE`, `DELETE`, `INSERT`, or `DROP` statements.\n    Also, for text values, use single quotes (e.g., 'value').\n\n    Example: 'What is the status of flight 6E815?'\n    Generated SQL: SELECT status FROM flights WHERE flight_no = '6E815';\n
    Example: 'Show available flights from Mumbai to Bengaluru.'\n    Generated SQL: SELECT * FROM flights WHERE origin = 'BOM' AND destination = 'BLR';\n
    Example: 'List flights from Delhi to Goa under ₹7000.'\n    Generated SQL: SELECT * FROM flights WHERE origin = 'DEL' AND destination = 'GOI' AND fare_inr < 7000;\n
    Example: 'Show flights delayed by more than 60 minutes.'\n    Generated SQL: SELECT * FROM flights WHERE delay_minutes > 60 AND status = 'Delayed';"""),
    ("human", "{query}")
])
sql_query_generation_chain = sql_query_generation_prompt | llm

# --- AI Agent for SQL Execution ---
tools = [sql_query_tool]
agent_executor = create_react_agent(llm, tools)

# --- LLM-based Spell Corrector and Query Enhancer ---
llm_spell_corrector = create_llm_spell_corrector(llm)
llm_query_enhancer = create_llm_query_enhancer(llm)


# --- RAG Setup (Pinecone) ---
PINECONE_INDEX_NAME = "airline-faq-index"
PINECONE_CLOUD = "aws" # Or your chosen cloud
PINECONE_REGION = "us-east-1" # Or your chosen region

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def setup_pinecone_vectorstore():
    pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    embedding_dimension = len(embeddings.embed_query("test")) # Get embedding dimension dynamically
    vectorstore = None

    try:
        # Attempt to create the index
        print(f"Attempting to create Pinecone index: {PINECONE_INDEX_NAME}")
        pinecone.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=embedding_dimension,
            metric='cosine',
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION)
        )
        print("Pinecone index created. Waiting for it to be ready...")
        # A more robust wait might check the index status via pinecone.describe_index
        while PINECONE_INDEX_NAME not in pinecone.list_indexes(): # This might still be flaky, but the try-except will catch if it exists
             time.sleep(1)

        # If creation was successful, load PDF and add documents
        try:
            loader = PyMuPDFLoader("data/Knowledge_Base_for_Airline_Info_and_FAQs.pdf")
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(docs)

            vectorstore = PineconeVectorStore.from_documents(
                documents=chunks,
                embedding=embeddings,
                index_name=PINECONE_INDEX_NAME
            )
            print(f"Successfully added {len(chunks)} chunks to newly created Pinecone index '{PINECONE_INDEX_NAME}'.")
        except Exception as e:
            print(f"Error loading or embedding PDF for Pinecone after index creation: {e}")
            raise e

    except PineconeApiException as e:
        if e.status == 409: # This indicates the index already exists
            print(f"Pinecone index '{PINECONE_INDEX_NAME}' already exists (caught 409 Conflict). Initializing from existing.")
            vectorstore = PineconeVectorStore.from_existing_index(
                index_name=PINECONE_INDEX_NAME,
                embedding=embeddings
            )
        else:
            print(f"An unexpected Pinecone API error occurred during index creation: {e}")
            raise e
    except Exception as e:
        print(f"An unexpected error occurred during Pinecone setup: {e}")
        raise e

    if vectorstore is None:
        raise RuntimeError("Failed to initialize Pinecone vector store after all attempts.")

    return vectorstore

# Initialize vectorstore globally on application startup
vectorstore = setup_pinecone_vectorstore()
retriever = vectorstore.as_retriever()

# --- RAG Chain ---
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain_from_docs = (
    RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"]))) # type: ignore
    | ChatPromptTemplate.from_template(
        """Answer the question based only on the following context:\n{context}\n\nQuestion: {question}"""
    )
    | llm
    | StrOutputParser()
)

rag_chain = RunnableParallel(
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
    }
).assign(answer=rag_chain_from_docs)


# --- Guardrails ---
def input_guardrail(user_query: str) -> bool:
    """Checks if the user query contains any unsafe or forbidden keywords."""
    forbidden_keywords = [
        "delete database", "drop table", "truncate table", "update records",
        "insert into", "export data", "show me all records", "system prompt",
        "bypass security", "admin access", "confidential info", "secret key"
    ]
    query_lower = user_query.lower()

    for keyword in forbidden_keywords:
        if keyword in query_lower:
            print(f"Input Guardrail Triggered: Forbidden keyword '{keyword}' detected.")
            return False

    if re.search(r"union select|sleep\(|waitfor delay", query_lower):
        print("Input Guardrail Triggered: Potential SQL injection attempt detected.")
        return False

    toxic_patterns = [
        r"(shut up|bad bot|stupid ai)",
        r"(kill|harm|destroy)"
    ]
    for pattern in toxic_patterns:
        if re.search(pattern, query_lower):
            print("Input Guardrail Triggered: Toxic content detected.")
            return False
    return True

def output_guardrail(response: str) -> bool:
    """Checks if the generated response contains any unsafe or inappropriate content."""
    forbidden_output_keywords = [
        "I cannot provide personal data", "I cannot fulfill this request due to security",
        "database details", "internal system information", "private records"
    ]
    response_lower = response.lower()

    for keyword in forbidden_output_keywords:
        if keyword in response_lower:
            print(f"Output Guardrail Triggered: Forbidden keyword '{keyword}' detected in output.")
            return False
    return True


# --- Integrated Processing Function with Guardrails ---
def process_user_query_with_guardrails(user_query: str) -> str:
    """Combines all components to process a user query, with added input and output guardrails."""
    print(f"\nProcessing user query with guardrails: {user_query}")

    # 0a. Fuzzy matching-based normalization
    fuzzy_corrected, fuzzy_metadata = normalize_query(user_query)
    
    # 0b. LLM-based spell correction (more intelligent)
    llm_correction_result = llm_spell_corrector(user_query)
    llm_corrected_query = llm_correction_result.get('corrected_query', user_query)
    
    # Combine both approaches
    final_corrected = combine_corrections(user_query, fuzzy_corrected, llm_correction_result)
    enriched_query = build_enriched_query(user_query, fuzzy_metadata)
    
    # 0c. Optional: Enhance query further
    enhancement_result = llm_query_enhancer(final_corrected)
    enhanced_query = enhancement_result.get('enhanced_query', final_corrected)
    
    print(f"Original query: {user_query}")
    print(f"Fuzzy corrected: {fuzzy_corrected}")
    print(f"LLM corrected: {llm_corrected_query}")
    print(f"Final corrected: {final_corrected}")
    print(f"Enhanced query: {enhanced_query}")
    if llm_correction_result.get('corrections'):
        print(f"Corrections applied: {llm_correction_result['corrections']}")

    # 1. Apply Input Guardrails
    if not input_guardrail(final_corrected):
        return "I cannot process this query due to safety concerns or forbidden content. Please rephrase your request."

    # 2. Classify the query
    classification_response = input_classifier_chain.invoke({'query': enhanced_query})
    classification = classification_response.content.strip()
    print(f"Query classified as: {classification}")

    final_response = ""

    if classification == 'Need SQL':
        print("Routing to SQL Agent...")
        generated_sql_response = sql_query_generation_chain.invoke({'query': enhanced_query})
        generated_sql = generated_sql_response.content.strip()
        print(f"Generated SQL: {generated_sql}")

        try:
            agent_output = agent_executor.invoke(
                {"messages": [HumanMessage(content=f"Execute the following SQL query to get flight information: {generated_sql}")]}
            )
            final_response = agent_output['messages'][-1].content
        except Exception as e:
            final_response = f"Error executing SQL query: {e}. Please try again or rephrase your query."

    elif classification == 'Non SQL':
        print("Routing to RAG Chain...")
        rag_output = rag_chain.invoke({"question": enhanced_query})
        final_response = rag_output['answer']

    elif classification == 'Out of Context':
        print("Routing to Out of Context handler...")
        fallback_response = llm.invoke(
            f"Your query '{enhanced_query}' is outside the scope of airline support. Can I help you with anything related to flights or airline policies?"
        )
        final_response = fallback_response.content

    else:
        final_response = "Unable to classify your query. Please rephrase it or ask about flights/policies."

    # 3. Apply Output Guardrails
    if not output_guardrail(final_response):
        return "I'm sorry, but I cannot provide this information. There was an issue with generating a safe and compliant response."

    print(f"Final Response: {final_response}")
    return final_response