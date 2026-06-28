"""
Spell correction and fuzzy matching utilities for handling misspelled user queries.
"""

from difflib import get_close_matches
from typing import Dict, Tuple

# Common airline misspellings and corrections
AIRLINE_CORRECTIONS = {
    "air india": ["AI", "air india"],
    "singapore": ["SG", "singapore airlines"],
    "indigo": ["IX", "indigo"],
    "vistara": ["UK", "vistara"],
    "spice jet": ["SG", "spicejet"],
    "go air": ["G8", "goair"],
    "british airways": ["BA", "british airways"],
    "emirates": ["EK", "emirates"],
}

# Common airport codes and their misspellings
AIRPORT_CODES = {
    "delhi": "DEL",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "goa": "GOI",
    "hyderabad": "HYD",
    "kolkata": "CCU",
    "delhi airport": "DEL",
    "bombay": "BOM",
    "blr airport": "BLR",
    "del airport": "DEL",
}

# Common airline-related keywords
COMMON_QUERIES = {
    "flight": ["flight", "flite", "flight"],
    "booking": ["booking", "bokking", "book"],
    "cancelled": ["cancelled", "canceled", "cancled"],
    "delayed": ["delayed", "delyed", "delay"],
    "available": ["available", "availble", "avaliable"],
    "schedule": ["schedule", "schedul", "sheduled"],
    "passenger": ["passenger", "pasanger", "passanger"],
    "luggage": ["luggage", "baggage", "lugage"],
    "refund": ["refund", "refund"],
    "ticket": ["ticket", "tikket"],
}


def correct_spelling(text: str, threshold: float = 0.8) -> str:
    """
    Attempts to correct spelling in the given text using fuzzy matching.
    
    Args:
        text: The input text to correct
        threshold: Minimum similarity ratio (0-1) for accepting corrections
        
    Returns:
        Corrected text
    """
    words = text.lower().split()
    corrected_words = []
    
    for word in words:
        # Check if word matches any common query keywords
        matched = False
        for correct_keyword, variations in COMMON_QUERIES.items():
            close_matches = get_close_matches(word, variations, n=1, cutoff=threshold)
            if close_matches:
                corrected_words.append(correct_keyword)
                matched = True
                break
        
        if not matched:
            corrected_words.append(word)
    
    return " ".join(corrected_words)


def fuzzy_match_airport(airport_input: str, threshold: float = 0.8) -> str:
    """
    Fuzzy match airport names/codes to standardized airport codes.
    
    Args:
        airport_input: User's airport input (potentially misspelled)
        threshold: Minimum similarity ratio for accepting a match
        
    Returns:
        Standardized airport code (e.g., 'DEL', 'BOM')
    """
    airport_lower = airport_input.lower().strip()
    
    # Direct lookup
    if airport_lower in AIRPORT_CODES:
        return AIRPORT_CODES[airport_lower]
    
    # Fuzzy matching
    matches = get_close_matches(airport_lower, AIRPORT_CODES.keys(), n=1, cutoff=threshold)
    if matches:
        return AIRPORT_CODES[matches[0]]
    
    # If no match found, return original (uppercase) - LLM will handle it
    return airport_input.upper()


def fuzzy_match_airline(airline_input: str, threshold: float = 0.8) -> str:
    """
    Fuzzy match airline names to standardized codes.
    
    Args:
        airline_input: User's airline input (potentially misspelled)
        threshold: Minimum similarity ratio for accepting a match
        
    Returns:
        Standardized airline code or name
    """
    airline_lower = airline_input.lower().strip()
    
    # Fuzzy matching
    matches = get_close_matches(airline_lower, AIRLINE_CORRECTIONS.keys(), n=1, cutoff=threshold)
    if matches:
        return AIRLINE_CORRECTIONS[matches[0]][0]  # Return airline code
    
    # If no match found, return original
    return airline_input


def normalize_query(query: str) -> Tuple[str, Dict]:
    """
    Normalize and correct a user query for better processing.
    
    Args:
        query: The raw user query
        
    Returns:
        Tuple of (corrected_query, metadata_dict)
    """
    # Correct spelling
    corrected = correct_spelling(query)
    
    # Extract potential airport codes and airline names for fuzzy matching
    words = corrected.split()
    metadata = {
        "original_query": query,
        "corrected_query": corrected,
        "airports": [],
        "airlines": [],
    }
    
    # Simple heuristic: words after "from", "to", "between" are likely airports
    airport_keywords = ["from", "to", "between", "origin", "destination"]
    for i, word in enumerate(words):
        if word in airport_keywords and i + 1 < len(words):
            next_word = words[i + 1]
            corrected_airport = fuzzy_match_airport(next_word)
            metadata["airports"].append(corrected_airport)
    
    # Words containing airline-related terms
    airline_keywords = ["airline", "carrier", "operator"]
    for word in words:
        if any(keyword in word.lower() for keyword in airline_keywords):
            corrected_airline = fuzzy_match_airline(word)
            metadata["airlines"].append(corrected_airline)
    
    return corrected, metadata


def build_enriched_query(query: str, metadata: Dict) -> str:
    """
    Build an enriched query with spelling corrections and normalized values.
    
    Args:
        query: Original query
        metadata: Metadata from normalize_query
        
    Returns:
        Enriched query ready for LLM processing
    """
    enriched = metadata["corrected_query"]
    
    # Add hints for LLM about corrections
    hints = []
    if metadata["airports"]:
        hints.append(f"Airports: {', '.join(metadata['airports'])}")
    if metadata["airlines"]:
        hints.append(f"Airlines: {', '.join(metadata['airlines'])}")
    
    if hints:
        enriched += f" [Corrections: {'; '.join(hints)}]"
    
    return enriched
