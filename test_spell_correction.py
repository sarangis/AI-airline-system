"""
Test script to demonstrate spell correction and fuzzy matching improvements
"""

from src.spell_corrector import correct_spelling, fuzzy_match_airport, fuzzy_match_airline, normalize_query, build_enriched_query

# Test cases with misspellings
test_queries = [
    "show me flights from mumbai to bengaluru",  # correct
    "show me flites from mumbi to bengalore",     # misspelled
    "list availble flites from delhi to goa",     # misspelled
    "show cancelld flights from blangalore",      # misspelled
    "find delayed flites",                        # misspelled
    "show flights from delh to bom tommorow",     # misspelled
]

print("=" * 80)
print("SPELL CORRECTION AND NORMALIZATION TEST")
print("=" * 80)

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"Test Case {i}:")
    print(f"Original Query: {query}")
    
    # Test spell correction
    corrected = correct_spelling(query)
    print(f"Corrected Query: {corrected}")
    
    # Test normalization
    normalized, metadata = normalize_query(query)
    print(f"Normalized Query: {normalized}")
    print(f"Metadata: {metadata}")
    
    # Test enriched query
    enriched = build_enriched_query(query, metadata)
    print(f"Enriched Query: {enriched}")


print(f"\n{'='*80}")
print("AIRPORT FUZZY MATCHING TEST")
print("=" * 80)

airport_tests = [
    ("mumbai", "BOM"),
    ("delhi", "DEL"),
    ("bengaluru", "BLR"),
    ("bangalore", "BLR"),
    ("mumbi", "BOM"),
    ("delh", "DEL"),
    ("goa", "GOI"),
]

for airport_input, expected in airport_tests:
    result = fuzzy_match_airport(airport_input)
    status = "✓" if result == expected else "✗"
    print(f"{status} Input: '{airport_input}' → Output: '{result}' (Expected: '{expected}')")


print(f"\n{'='*80}")
print("AIRLINE FUZZY MATCHING TEST")
print("=" * 80)

airline_tests = [
    ("air india", "AI"),
    ("singapore", "SG"),
    ("indigo", "IX"),
    ("singapore airlines", "SG"),
]

for airline_input, expected in airline_tests:
    result = fuzzy_match_airline(airline_input)
    print(f"Input: '{airline_input}' → Output: '{result}'")
