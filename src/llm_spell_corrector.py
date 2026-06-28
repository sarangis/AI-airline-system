"""
LLM-based spell correction and query enhancement for the airline system.
Uses the language model to intelligently handle misspellings and improve query clarity.
"""

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re


def create_llm_spell_corrector(llm):
    """
    Creates an LLM-based spell corrector that understands airline domain context.
    
    Args:
        llm: The language model instance (e.g., ChatOpenAI)
        
    Returns:
        A function that corrects and enhances queries
    """
    
    correction_prompt = PromptTemplate.from_template(
        """You are an expert spell checker for an airline customer support system.
Your task is to correct misspellings, typos, and grammar issues in user queries while preserving the user's intent.

DOMAIN CONTEXT:
- Airline terminology: flights, booking, cancellation, delay, refund, luggage, terminal, gate, etc.
- Airport codes: DEL (Delhi), BOM (Mumbai), BLR (Bangalore), GOI (Goa), HYD (Hyderabad), CCU (Kolkata), etc.
- Airlines: Air India (AI), Singapore Airlines (SG), IndiGo (IX), Vistara (UK), SpiceJet, GoAir, etc.
- Common issues: delays, cancellations, rebooking, refunds, baggage allowance, check-in procedures

USER QUERY: "{query}"

TASKS:
1. Identify and correct ALL misspellings and typos
2. Normalize airport names to standard codes (e.g., "mumbai" → "BOM")
3. Normalize airline names to standard codes (e.g., "air india" → "AI")
4. Fix grammatical errors
5. Clarify ambiguous terms using airline domain knowledge
6. Preserve the original intent and sentiment

Return ONLY a valid JSON object with this exact structure (no markdown, no code blocks):
{{
  "original_query": "the original user query",
  "corrected_query": "the corrected and normalized query",
  "corrections": [
    "correction 1",
    "correction 2"
  ],
  "confidence": 0.95,
  "extracted_entities": {{
    "airports": ["DEL", "BOM"],
    "airlines": ["AI"],
    "keywords": ["flight", "booking", "delay"]
  }}
}}

IMPORTANT:
- Return ONLY the JSON object, no additional text
- Use standard 3-letter airport codes in extracted_entities
- Be conservative: if unsure about a word, keep it as-is
- Include all corrections made in the corrections array
- Confidence should be between 0 and 1"""
    )
    
    correction_chain = correction_prompt | llm | StrOutputParser()
    
    def correct_query(query: str) -> dict:
        """
        Correct misspellings and enhance the query using LLM.
        
        Args:
            query: The original user query (potentially with misspellings)
            
        Returns:
            Dictionary with corrected query, corrections, and extracted entities
        """
        try:
            result = correction_chain.invoke({'query': query})
            
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                correction_data = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                correction_data = {
                    "original_query": query,
                    "corrected_query": query,
                    "corrections": [],
                    "confidence": 0.0,
                    "extracted_entities": {
                        "airports": [],
                        "airlines": [],
                        "keywords": []
                    }
                }
            
            return correction_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in spell correction: {e}")
            return {
                "original_query": query,
                "corrected_query": query,
                "corrections": [],
                "confidence": 0.0,
                "extracted_entities": {
                    "airports": [],
                    "airlines": [],
                    "keywords": []
                }
            }
        except Exception as e:
            print(f"Error in LLM spell correction: {e}")
            return {
                "original_query": query,
                "corrected_query": query,
                "corrections": [],
                "confidence": 0.0,
                "extracted_entities": {
                    "airports": [],
                    "airlines": [],
                    "keywords": []
                }
            }
    
    return correct_query


def create_llm_query_enhancer(llm):
    """
    Creates an LLM-based query enhancer that makes queries more specific and structured.
    
    Args:
        llm: The language model instance
        
    Returns:
        A function that enhances queries for better processing
    """
    
    enhancement_prompt = PromptTemplate.from_template(
        """You are a query enhancement specialist for an airline support system.
Your task is to enhance user queries to make them clearer and more structured for processing.

USER QUERY: "{query}"

ENHANCEMENT TASKS:
1. Add missing context if identifiable from the query
2. Make implicit requests explicit
3. Normalize date references (e.g., "tommorow" → "tomorrow", "next week" → specific dates if possible)
4. Suggest the most relevant information to include

Return a JSON object with:
{{
  "enhanced_query": "the improved query",
  "suggested_clarifications": ["clarification 1", "clarification 2"],
  "query_type": "flight_search|flight_status|booking|cancellation|refund|other",
  "urgency": "high|medium|low",
  "required_info": ["field1", "field2"]
}}

IMPORTANT:
- Return ONLY the JSON object, no additional text
- Keep the enhanced query user-friendly
- Be helpful but not overly verbose"""
    )
    
    enhancement_chain = enhancement_prompt | llm | StrOutputParser()
    
    def enhance_query(query: str) -> dict:
        """
        Enhance the query for better processing.
        
        Args:
            query: The user query
            
        Returns:
            Dictionary with enhanced query and metadata
        """
        try:
            result = enhancement_chain.invoke({'query': query})
            
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                enhancement_data = json.loads(json_match.group())
            else:
                enhancement_data = {
                    "enhanced_query": query,
                    "suggested_clarifications": [],
                    "query_type": "other",
                    "urgency": "medium",
                    "required_info": []
                }
            
            return enhancement_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in query enhancement: {e}")
            return {
                "enhanced_query": query,
                "suggested_clarifications": [],
                "query_type": "other",
                "urgency": "medium",
                "required_info": []
            }
        except Exception as e:
            print(f"Error in LLM query enhancement: {e}")
            return {
                "enhanced_query": query,
                "suggested_clarifications": [],
                "query_type": "other",
                "urgency": "medium",
                "required_info": []
            }
    
    return enhance_query


def combine_corrections(original_query: str, fuzzy_corrected: str, llm_corrected: dict) -> str:
    """
    Combines fuzzy matching and LLM corrections to get the best result.
    
    Args:
        original_query: Original query
        fuzzy_corrected: Result from fuzzy matching
        llm_corrected: Result from LLM correction
        
    Returns:
        Best corrected query
    """
    # Use LLM correction if confidence is high, otherwise use fuzzy matching
    if llm_corrected.get('confidence', 0) > 0.7:
        return llm_corrected.get('corrected_query', fuzzy_corrected)
    else:
        return fuzzy_corrected
