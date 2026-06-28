"""
Test script to demonstrate LLM-based spell correction
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.llm_spell_corrector import create_llm_spell_corrector, create_llm_query_enhancer

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Create correctors
spell_corrector = create_llm_spell_corrector(llm)
query_enhancer = create_llm_query_enhancer(llm)

# Test cases
test_queries = [
    "show me flites from mumbi to bengalore",
    "i want to cancel my booking on spice jet",
    "are there any delayed flights tommorow from delhi?",
    "refund my ticked from air india",
    "list all cancled flights from bombay",
]

print("=" * 80)
print("LLM-BASED SPELL CORRECTION TEST")
print("=" * 80)

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"Test Case {i}: {query}")
    print(f"{'='*80}")
    
    # Spell correction
    print("\nSpell Correction:")
    correction_result = spell_corrector(query)
    print(f"  Corrected: {correction_result.get('corrected_query')}")
    print(f"  Confidence: {correction_result.get('confidence', 0):.2f}")
    if correction_result.get('corrections'):
        print(f"  Corrections: {correction_result['corrections']}")
    
    entities = correction_result.get('extracted_entities', {})
    if entities.get('airports'):
        print(f"  Airports: {entities['airports']}")
    if entities.get('airlines'):
        print(f"  Airlines: {entities['airlines']}")
    
    # Query enhancement
    print("\nQuery Enhancement:")
    enhanced_result = query_enhancer(correction_result.get('corrected_query'))
    print(f"  Enhanced: {enhanced_result.get('enhanced_query')}")
    print(f"  Query Type: {enhanced_result.get('query_type')}")
    if enhanced_result.get('suggested_clarifications'):
        print(f"  Clarifications: {enhanced_result['suggested_clarifications']}")

print(f"\n{'='*80}")
print("Test completed!")
