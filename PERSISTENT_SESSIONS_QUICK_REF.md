# Persistent Sessions Quick Reference

## Quick Start

### 1. Start a New Session
```bash
curl -X POST http://localhost:8000/new-session \
  -H "Content-Type: application/json" \
  -d '{"user_name": "John"}'
```
Returns: `session_id`

### 2. Send a Query (Auto-Creates Session if Needed)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me flights to goa",
    "session_id": "abc-123",
    "user_name": "John"
  }'
```

### 3. List All Conversations
```bash
# All sessions
curl http://localhost:8000/sessions

# By user
curl http://localhost:8000/sessions?user_name=John&limit=10

# Get stats
curl http://localhost:8000/sessions/stats
```

### 4. Resume a Previous Session
```bash
curl -X POST http://localhost:8000/resume-session/session-001 \
  -H "Content-Type: application/json"
```

### 5. Search Conversations
```bash
curl "http://localhost:8000/search-sessions?keyword=delhi"
```

### 6. Delete a Session
```bash
curl -X DELETE http://localhost:8000/session/session-001
```

## Python Example

```python
import requests

BASE_URL = "http://localhost:8000"
session_id = None

# 1. Start new session
response = requests.post(f"{BASE_URL}/new-session", json={"user_name": "John"})
session_id = response.json()["session_id"]
print(f"Session created: {session_id}")

# 2. Send query
response = requests.post(f"{BASE_URL}/query", json={
    "query": "show me flights to goa",
    "session_id": session_id
})
print(response.json()["message"])

# 3. Continue conversation (same session_id)
response = requests.post(f"{BASE_URL}/query", json={
    "query": "book the cheapest",
    "session_id": session_id
})
print(response.json()["message"])

# 4. List all sessions later
response = requests.get(f"{BASE_URL}/sessions")
print(f"Total sessions: {response.json()['total_count']}")

# 5. Resume later
response = requests.post(f"{BASE_URL}/resume-session/{session_id}")
print(response.json()["message"])
```

## JavaScript/React Example

```javascript
const BASE_URL = 'http://localhost:8000';

async function startNewSession(userName) {
  const res = await fetch(`${BASE_URL}/new-session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_name: userName })
  });
  return res.json();
}

async function sendQuery(query, sessionId) {
  const res = await fetch(`${BASE_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id: sessionId })
  });
  return res.json();
}

async function listSessions() {
  const res = await fetch(`${BASE_URL}/sessions`);
  return res.json();
}

async function resumeSession(sessionId) {
  const res = await fetch(`${BASE_URL}/resume-session/${sessionId}`, {
    method: 'POST'
  });
  return res.json();
}

// Usage
const session = await startNewSession('John');
const response = await sendQuery('flights to goa', session.session_id);
console.log(response.message);
```

## Endpoint Summary

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/new-session` | POST | Start fresh session | Clear separation, no context |
| `/query` | POST | Send query | Creates session if needed |
| `/chat` | POST | Alias for /query | Same functionality |
| `/sessions` | GET | List all sessions | Filter by user, limit |
| `/session/{id}` | GET | Get session details | Returns metadata |
| `/session/{id}` | DELETE | Delete session | Removes from memory & storage |
| `/resume-session/{id}` | POST | Resume old session | Loads full history |
| `/search-sessions` | GET | Search by keyword | Searches user, booking ref, summary |
| `/sessions/stats` | GET | Get statistics | Total sessions, messages, users |
| `/greeting` | GET | Get greeting | Initial message |
| `/clarify` | POST | Ask for clarification | When query is ambiguous |
| `/health` | GET | API health | Check if running |

## Typical Conversation Flow

```
1. POST /new-session
   └─ Get session_id

2. POST /query (multiple times)
   └─ Continue conversation
   └─ Auto-saved after each query

3. [User closes browser]

4. GET /sessions
   └─ See all previous conversations

5. POST /resume-session/{session_id}
   └─ Welcome back message
   └─ Full history loaded

6. POST /query (continue from where we left off)
   └─ LLM has access to all previous messages
   └─ Better context-aware responses
```

## Key Points

✓ **New Session = Clear Start**: No previous context
✓ **Query Continues**: Same session_id keeps context
✓ **Auto-Save**: Every response auto-saved
✓ **Resume Anytime**: Load any old session
✓ **Full History**: All messages available for context
✓ **Search**: Find conversations by keywords
✓ **Persistent**: Survives server restarts

## Storage Location

Conversations saved in: `data/conversations/`

Structure:
```
data/conversations/
├── index.json          (quick reference for all sessions)
├── session-001.json    (session data)
├── session-002.json    (session data)
└── ...
```

## Response Types

### New Session Response
```json
{
  "session_id": "abc-123-def",
  "message": "greeting text",
  "status": "new_session_started"
}
```

### Query Response
```json
{
  "message": "conversational response",
  "original_response": "technical response",
  "session_id": "abc-123-def",
  "timestamp": "2024-06-28T10:05:00",
  "follow_up_suggestion": "optional suggestion",
  "is_new_session": false
}
```

### Sessions List Response
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
    }
  ],
  "total_count": 1
}
```

## Tips

1. **Always save session_id** - You need it to continue
2. **Use session_id without quotes** - Pass as string
3. **Search for old conversations** - Use /search-sessions
4. **Check stats** - /sessions/stats shows usage
5. **Delete if needed** - Use DELETE /session/{id}

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Session not found" | Use valid session_id from /sessions list |
| Lost session_id | Use /sessions to list all, then /resume-session |
| Data not saved | Automatically saved after each query |
| Storage full | Delete old sessions with DELETE endpoint |
| Can't resume | Check session exists with GET /sessions |

## Advanced Usage

### Mass Search
```bash
curl "http://localhost:8000/search-sessions?keyword=refund" \
  | jq '.sessions | length'
```

### Get All User Sessions
```bash
curl "http://localhost:8000/sessions?user_name=John&limit=100" \
  | jq '.sessions[].session_id'
```

### Session Statistics
```bash
curl http://localhost:8000/sessions/stats
```

Result:
```json
{
  "total_sessions": 42,
  "total_messages": 156,
  "unique_users": 8,
  "storage_path": "data/conversations"
}
```

## Limits

- Max messages in memory: 100 per session (older kept in storage)
- Max sessions listed: 20 (adjustable)
- Search: Checks user_name, booking_ref, summary
- Storage: Unlimited (disk space dependent)

## Session Lifecycle

```
1. Create
   POST /new-session or POST /query

2. Use
   POST /query (auto-saves after each query)

3. Resume
   POST /resume-session/{id}

4. Search
   GET /search-sessions?keyword=...

5. Delete (optional)
   DELETE /session/{id}
```

## Best Practices

1. **Use descriptive user_name** - For easy search
2. **Include booking_ref** - For tracking
3. **Start new session** - For unrelated topics
4. **Resume when possible** - For continuity
5. **Regular cleanup** - Delete old sessions
6. **Search before asking** - Find old conversations
7. **Monitor stats** - Track usage patterns

---

For detailed documentation, see: `PERSISTENT_SESSIONS.md`
