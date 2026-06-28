# Persistent Conversation Sessions

## Overview
Enhanced the conversational system with persistent storage. Users can now:
- Resume previous conversations
- Keep full conversation history
- Start brand new sessions anytime
- Search through past conversations
- View conversation statistics

## Key Features

### 1. **Full Conversation Persistence**
All conversations are automatically saved to disk with:
- Complete message history
- User profile information
- Booking references
- Timestamps
- Conversation summaries

### 2. **Resume Previous Conversations**
Load any previous session and continue where you left off:
```bash
POST /resume-session/{session_id}
```

The system automatically:
- Loads the full conversation history
- Maintains context from all previous messages
- Generates a "welcome back" message with summary

### 3. **Start New Sessions**
Explicitly start a fresh conversation anytime:
```bash
POST /new-session
```

Benefits:
- Clear separation between different topics/bookings
- No context pollution from previous chats
- Dedicated session for each new issue

### 4. **Search & Filter Sessions**
Find previous conversations by:
- User name
- Booking reference
- Conversation content
- Keywords

### 5. **Session Statistics**
Monitor usage with:
- Total sessions count
- Total messages count
- Unique users count
- Storage location

## Architecture

```
User Request
    ↓
API Endpoint
    ├─ Check if session in memory
    ├─ If not, load from storage
    └─ Create if doesn't exist
    ↓
Process Query
    ├─ Use FULL conversation history
    ├─ Generate contextual response
    └─ Update conversation
    ↓
Save to Storage
    ├─ Save messages
    ├─ Update index
    └─ Persist to disk
    ↓
Return Response + Session ID
```

## Storage Structure

```
data/
└── conversations/
    ├── index.json (metadata for all sessions)
    ├── session-001.json (session data)
    ├── session-002.json (session data)
    └── ...
```

### Session File Example
```json
{
  "session_id": "abc-123-def",
  "session_start": "2024-06-28T10:00:00",
  "user_name": "John",
  "booking_ref": "AI2024001",
  "message_count": 5,
  "summary": "Topics discussed: flight, booking",
  "messages": [
    {
      "timestamp": "2024-06-28T10:01:00",
      "role": "user",
      "content": "show me flights to goa",
      "metadata": {}
    },
    ...
  ]
}
```

### Index File Example
```json
{
  "session-001": {
    "user_name": "Priya",
    "booking_ref": "AI2024001",
    "message_count": 4,
    "session_start": "2024-06-28T10:00:00",
    "summary": "Topics discussed: flight",
    "last_updated": "2024-06-28T10:05:00"
  },
  ...
}
```

## API Endpoints

### 1. **POST /new-session**
Start a completely new conversation session.

**Request:**
```bash
POST /new-session
{
  "user_name": "John"  // optional
}
```

**Response:**
```json
{
  "session_id": "xyz-789-abc",
  "message": "Hello! I'm your airline support assistant. How can I help you today?",
  "status": "new_session_started"
}
```

### 2. **POST /query**
Send a query (creates new session if needed, or continues existing).

**Request:**
```bash
POST /query
{
  "query": "show me flights to goa",
  "session_id": "optional-id",  // omit to create new session
  "user_name": "John",           // optional
  "booking_ref": "AI2024001"     // optional
}
```

**Response:**
```json
{
  "message": "Great! I found 5 flights to Goa...",
  "original_response": "[technical data]",
  "session_id": "xyz-789-abc",
  "timestamp": "2024-06-28T10:05:00",
  "follow_up_suggestion": "Would you like to book?",
  "is_new_session": false
}
```

### 3. **GET /sessions**
List all saved sessions.

**Request:**
```bash
GET /sessions?limit=20&user_name=John  // both optional
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "session-001",
      "user_name": "John",
      "booking_ref": "AI2024001",
      "message_count": 5,
      "session_start": "2024-06-28T10:00:00",
      "summary": "Topics discussed: flight, booking",
      "last_updated": "2024-06-28T10:05:00"
    },
    ...
  ],
  "total_count": 3
}
```

### 4. **GET /session/{session_id}**
Get detailed information about a specific session.

**Response:**
```json
{
  "session_id": "session-001",
  "message_count": 5,
  "user_name": "John",
  "booking_ref": "AI2024001",
  "session_start": "2024-06-28T10:00:00",
  "summary": "Topics discussed: flight, booking"
}
```

### 5. **POST /resume-session/{session_id}**
Resume a previous conversation.

**Response:**
```json
{
  "session_id": "session-001",
  "message": "Welcome back, John! I see we last talked about flights, booking. How can I help you today?",
  "status": "session_resumed",
  "previous_message_count": 5,
  "summary": "Topics discussed: flight, booking"
}
```

### 6. **GET /search-sessions**
Search conversations by keyword.

**Request:**
```bash
GET /search-sessions?keyword=delhi
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "session-002",
      "user_name": "Priya",
      "summary": "Topics discussed: flight, booking",
      "message_count": 7,
      ...
    }
  ],
  "total_count": 2
}
```

### 7. **GET /sessions/stats**
Get conversation statistics.

**Response:**
```json
{
  "total_sessions": 15,
  "total_messages": 127,
  "unique_users": 8,
  "storage_path": "data/conversations"
}
```

### 8. **DELETE /session/{session_id}**
Delete a conversation session.

**Response:**
```json
{
  "status": "success",
  "message": "Session cleared"
}
```

## Example Conversation Flows

### Flow 1: New Session → Continue → Resume Later

```
DAY 1, MORNING:
1. POST /new-session
   Response: session_id = "abc-123"
   
2. POST /query
   {query: "show flights to goa", session_id: "abc-123"}
   Response: Flights listed
   
3. POST /query
   {query: "book AI401", session_id: "abc-123"}
   Response: Booking confirmed
   
[Session auto-saved]

LATER:
GET /sessions
Response: Shows "abc-123" in list

POST /resume-session/abc-123
Response: "Welcome back! Last we discussed flights, booking..."

POST /query
{query: "what's my booking status?", session_id: "abc-123"}
Response: Uses full history for context
```

### Flow 2: Multi-User with Search

```
User "John" makes bookings:
POST /new-session {user_name: "John"}
POST /query {query: "..."}  // Multiple queries
Result: Session "john-session-1"

User "Priya" makes booking:
POST /new-session {user_name: "Priya"}
POST /query {query: "..."}
Result: Session "priya-session-1"

Later, admin searches:
GET /search-sessions?keyword=Delhi
Response: Shows all sessions discussing Delhi

GET /sessions?user_name=John
Response: Shows all John's sessions
```

### Flow 3: Resume Previous Session

```
John's old session: "session-001"
Message count: 15

GET /sessions
Response: Lists session-001

POST /resume-session/session-001
Response: "Welcome back, John! I see we last talked about flights, booking..."

POST /query
{query: "what was the flight number?", session_id: "session-001"}
Response: Uses all 15 previous messages for context
```

## Context Usage

### Before (Limited Context)
```
System remembers only: Last 5 messages
Limitation: Cannot recall earlier details
```

### After (Full Context)
```
System remembers: ALL messages in the session
Benefit: Can answer "what was the flight number?" from message #3
```

## Implementation Details

### Memory vs Storage
- **Memory**: Current sessions (fast access)
- **Storage**: All sessions (persistent, searchable)

When session is accessed:
1. Check if in memory (fast)
2. If not, load from storage (automatic)
3. Put in memory for faster access

### Automatic Saving
Every query response triggers:
```python
store.save_conversation(session_id, conversation.to_dict())
```

### Garbage Collection
Old conversations stay on disk forever. Optional cleanup:
```python
# Delete sessions older than 30 days
for session in sessions:
    age = datetime.now() - parse(session['last_updated'])
    if age > timedelta(days=30):
        store.delete_conversation(session_id)
```

## Files Created/Modified

- **Created**: `src/conversation_store.py` - Persistence layer
- **Modified**: `src/conversation_manager.py` - Enhanced with session tracking
- **Modified**: `api/main.py` - Added 8 new endpoints
- **Created**: `test_persistent_sessions.py` - Test suite

## Configuration

### Storage Location
Default: `data/conversations/`

To change:
```python
store = ConversationStore("path/to/storage")
```

### Max Messages in Memory
```python
conversation = ConversationHistory(max_history=100)
```

### Auto-Delete Old Sessions
```python
# In a background job
for session in store.list_sessions(limit=1000):
    age = datetime.now() - parse(session['last_updated'])
    if age > timedelta(days=90):
        store.delete_conversation(session['session_id'])
```

## Migration to Database

Current: File-based storage
Future: Database storage

```python
class ConversationStoreDB:
    def save_conversation(self, session_id, data):
        db.conversations.upsert(
            {"session_id": session_id},
            data
        )
    
    def load_conversation(self, session_id):
        return db.conversations.find_one({"session_id": session_id})
```

## Testing

Run the test suite:
```bash
python test_persistent_sessions.py
```

Tests:
- ✓ Create and save conversations
- ✓ Load conversations from storage
- ✓ List sessions
- ✓ Filter by user
- ✓ Search by keyword
- ✓ Get statistics
- ✓ Resume conversations
- ✓ Delete sessions
- ✓ Continue loaded conversations

## Benefits

✅ **Full History** - Remember all previous messages
✅ **Resume Anytime** - Pick up where you left off
✅ **New Sessions** - Start fresh anytime
✅ **Search** - Find old conversations easily
✅ **Persistent** - Survives server restarts
✅ **Multi-User** - Manage multiple users' sessions
✅ **Statistics** - Monitor usage patterns
✅ **Context-Aware** - LLM uses full history for better responses

## Troubleshooting

### Session Not Found
```
POST /query with invalid session_id
Response: 404 Not Found

Solution: Use GET /sessions to list valid session IDs
```

### Storage Full
```
Solution 1: Delete old conversations
Solution 2: Archive to database
Solution 3: Implement cleanup job
```

### Lost Sessions After Restart
```
Conversations are saved to disk
They will be loaded automatically when accessed
Current in-memory cache is cleared on restart (expected)
```
