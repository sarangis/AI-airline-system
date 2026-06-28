"""
Test script for conversational messaging features
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.conversation_manager import (
    ConversationHistory,
    create_conversational_response_formatter,
    create_greeting_generator,
    create_clarification_asker,
    create_session_summarizer,
    build_conversational_response
)

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Initialize conversation tools
response_formatter = create_conversational_response_formatter(llm)
greeting_generator = create_greeting_generator(llm)
clarification_asker = create_clarification_asker(llm)
session_summarizer = create_session_summarizer(llm)

print("=" * 80)
print("CONVERSATIONAL MESSAGING FEATURES TEST")
print("=" * 80)

# Test 1: Greeting
print("\n1. GREETING GENERATION")
print("-" * 80)
greeting = greeting_generator()
print(f"Greeting: {greeting}\n")

# Test 2: Conversation History
print("2. CONVERSATION HISTORY MANAGEMENT")
print("-" * 80)
conversation = ConversationHistory()
conversation.user_name = "John"
conversation.booking_ref = "AI2024001"

conversation.add_message("user", "show me flights from delhi to mumbai")
conversation.add_message("assistant", "Here are available flights...")
conversation.add_message("user", "can you help me book one?")
conversation.add_message("assistant", "I'd be happy to help you book...")

print(f"User: {conversation.user_name}")
print(f"Booking Reference: {conversation.booking_ref}")
print(f"Total messages: {len(conversation.messages)}")
print("\nConversation Context:")
print(conversation.get_conversation_context())

# Test 3: Response Formatting
print("\n3. RESPONSE FORMATTING (Technical → Conversational)")
print("-" * 80)

technical_response = """[
  {"flight_no": "AI101", "departure": "06:00", "arrival": "08:00", "duration": "2h", "price": 3500},
  {"flight_no": "AI201", "departure": "12:00", "arrival": "14:00", "duration": "2h", "price": 4000},
  {"flight_no": "AI301", "departure": "18:00", "arrival": "20:00", "duration": "2h", "price": 3800}
]"""

formatted_response = response_formatter(
    technical_response,
    conversation,
    "show me flights from delhi to mumbai"
)

print("Technical Response (Raw SQL/Data):")
print(technical_response[:100] + "...")
print("\nFormatted Response (Conversational):")
print(formatted_response)

# Test 4: Clarification Questions
print("\n4. CLARIFICATION QUESTIONS")
print("-" * 80)

ambiguous_queries = [
    "i want to change my flight",
    "show me available options",
    "what about refunds?",
]

for query in ambiguous_queries:
    print(f"Query: {query}")
    clarifications = clarification_asker(query)
    print(f"Clarifications:\n{clarifications}\n")

# Test 5: Complete Conversation Flow
print("5. COMPLETE CONVERSATION FLOW")
print("-" * 80)

conv_flow = ConversationHistory()
conv_flow.user_name = "Priya"

queries_and_responses = [
    {
        "query": "hi, can you help me find flights?",
        "response": "I found 5 flights available for you today from Delhi."
    },
    {
        "query": "show me the cheapest options",
        "response": "The cheapest flight is AI401 at ₹2,500, departing at 6:00 AM."
    },
    {
        "query": "what's the latest flight?",
        "response": "The latest flight is AI801 at ₹3,200, departing at 8:00 PM."
    },
    {
        "query": "i'll book the 6am flight",
        "response": "Great! I've booked AI401 for you. Your booking reference is: AI2024XYZ"
    }
]

for i, exchange in enumerate(queries_and_responses, 1):
    print(f"\n--- Exchange {i} ---")
    
    # User message
    conv_flow.add_message("user", exchange["query"])
    print(f"👤 User: {exchange['query']}")
    
    # Formatted response
    formatted = response_formatter(
        exchange["response"],
        conv_flow,
        exchange["query"]
    )
    conv_flow.add_message("assistant", formatted)
    print(f"🤖 Assistant: {formatted}")

# Test 6: Session Summary
print("\n6. SESSION SUMMARY")
print("-" * 80)
summary = session_summarizer(conv_flow)
print(summary)

# Test 7: Session Information
print("\n7. SESSION INFORMATION")
print("-" * 80)
session_dict = conv_flow.to_dict()
print(f"Session Start: {session_dict['session_start']}")
print(f"User: {session_dict['user_name']}")
print(f"Total Messages: {session_dict['message_count']}")
print(f"Booking Reference: {session_dict['booking_ref']}")

print("\n" + "=" * 80)
print("Test completed!")
print("=" * 80)
