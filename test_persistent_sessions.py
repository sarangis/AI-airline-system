"""
Test script for persistent conversation sessions
Demonstrates starting new sessions, resuming old ones, and searching conversations
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.conversation_manager import ConversationHistory, create_conversational_response_formatter
from src.conversation_store import ConversationStore

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

response_formatter = create_conversational_response_formatter(llm)
store = ConversationStore("data/conversations")

print("=" * 80)
print("PERSISTENT CONVERSATION SESSIONS TEST")
print("=" * 80)

# Test 1: Create and save a conversation
print("\n1. CREATE AND SAVE CONVERSATION SESSION")
print("-" * 80)

conv1 = ConversationHistory(session_id="session-001")
conv1.user_name = "Priya"
conv1.booking_ref = "AI2024001"

conv1.add_message("user", "show me flights to goa")
conv1.add_message("assistant", "I found 5 flights to Goa available tomorrow")
conv1.add_message("user", "which one is cheapest?")
conv1.add_message("assistant", "The cheapest is AI401 at ₹2,500")

# Save to storage
store.save_conversation("session-001", conv1.to_dict())
print(f"✅ Saved conversation 'session-001' for {conv1.user_name}")
print(f"   Messages: {len(conv1.messages)}")
print(f"   Summary: {conv1.get_summary()}")

# Test 2: Create another conversation
print("\n2. CREATE SECOND CONVERSATION SESSION")
print("-" * 80)

conv2 = ConversationHistory(session_id="session-002")
conv2.user_name = "Rajesh"
conv2.booking_ref = "AI2024002"

conv2.add_message("user", "i want to cancel my flight")
conv2.add_message("assistant", "I can help with your cancellation. Please provide your booking reference")
conv2.add_message("user", "AI2024002")
conv2.add_message("assistant", "I found your booking. Would you like a refund or rebooking?")

store.save_conversation("session-002", conv2.to_dict())
print(f"✅ Saved conversation 'session-002' for {conv2.user_name}")
print(f"   Messages: {len(conv2.messages)}")
print(f"   Summary: {conv2.get_summary()}")

# Test 3: Create third conversation
print("\n3. CREATE THIRD CONVERSATION SESSION")
print("-" * 80)

conv3 = ConversationHistory(session_id="session-003")
conv3.user_name = "Priya"
conv3.booking_ref = "AI2024003"

conv3.add_message("user", "what's your baggage policy?")
conv3.add_message("assistant", "We allow 1 checked bag (20kg) and 1 carry-on (7kg)")
conv3.add_message("user", "can i carry a laptop in carry-on?")
conv3.add_message("assistant", "Yes, laptops are allowed in carry-on baggage")

store.save_conversation("session-003", conv3.to_dict())
print(f"✅ Saved conversation 'session-003' for {conv3.user_name}")
print(f"   Messages: {len(conv3.messages)}")
print(f"   Summary: {conv3.get_summary()}")

# Test 4: List all sessions
print("\n4. LIST ALL SESSIONS")
print("-" * 80)

sessions = store.list_sessions(limit=10)
print(f"📋 Total sessions stored: {len(sessions)}")
for i, session in enumerate(sessions, 1):
    print(f"\n{i}. Session: {session['session_id']}")
    print(f"   User: {session.get('user_name', 'Unknown')}")
    print(f"   Booking Ref: {session.get('booking_ref', 'N/A')}")
    print(f"   Messages: {session.get('message_count', 0)}")
    print(f"   Summary: {session.get('summary', '')}")
    print(f"   Last Updated: {session.get('last_updated', 'N/A')}")

# Test 5: Filter sessions by user
print("\n5. FILTER SESSIONS BY USER")
print("-" * 80)

priya_sessions = store.list_sessions(user_name="Priya")
print(f"🔍 Sessions for user 'Priya': {len(priya_sessions)}")
for session in priya_sessions:
    print(f"   - {session['session_id']}: {session.get('summary', '')}")

# Test 6: Search conversations
print("\n6. SEARCH CONVERSATIONS")
print("-" * 80)

search_results = store.search_conversations("flight")
print(f"🔎 Search results for 'flight': {len(search_results)} sessions")
for result in search_results:
    print(f"   - {result['session_id']}: {result.get('summary', '')}")

print("\n")
search_results = store.search_conversations("cancel")
print(f"🔎 Search results for 'cancel': {len(search_results)} sessions")
for result in search_results:
    print(f"   - {result['session_id']}: {result.get('summary', '')}")

# Test 7: Load conversation from storage
print("\n7. LOAD CONVERSATION FROM STORAGE")
print("-" * 80)

loaded_data = store.load_conversation("session-001")
loaded_conv = ConversationHistory(session_id="session-001")
loaded_conv.from_dict(loaded_data)

print(f"✅ Loaded conversation 'session-001'")
print(f"   User: {loaded_conv.user_name}")
print(f"   Booking Ref: {loaded_conv.booking_ref}")
print(f"   Messages: {len(loaded_conv.messages)}")
print(f"   Context:\n{loaded_conv.get_conversation_context()}")

# Test 8: Continue loaded conversation
print("\n8. CONTINUE LOADED CONVERSATION")
print("-" * 80)

loaded_conv.add_message("user", "book the flight for me")
loaded_conv.add_message("assistant", "Booking confirmed! Your reference is AI2024GHI")

# Save updated conversation
store.save_conversation("session-001", loaded_conv.to_dict())
print(f"✅ Updated and saved conversation")
print(f"   New message count: {len(loaded_conv.messages)}")
print(f"   Updated summary: {loaded_conv.get_summary()}")

# Test 9: Get statistics
print("\n9. CONVERSATION STATISTICS")
print("-" * 80)

stats = store.get_session_stats()
print(f"📊 Statistics:")
print(f"   Total Sessions: {stats['total_sessions']}")
print(f"   Total Messages: {stats['total_messages']}")
print(f"   Unique Users: {stats['unique_users']}")
print(f"   Storage Path: {stats['storage_path']}")

# Test 10: Delete a conversation
print("\n10. DELETE A CONVERSATION")
print("-" * 80)

deleted = store.delete_conversation("session-003")
if deleted:
    print(f"✅ Deleted conversation 'session-003'")
else:
    print(f"❌ Failed to delete conversation")

remaining = store.list_sessions()
print(f"   Remaining sessions: {len(remaining)}")

print("\n" + "=" * 80)
print("Test completed!")
print("=" * 80)
print("\nConversations are saved in: data/conversations/")
print("You can resume any conversation by loading it from storage.")
