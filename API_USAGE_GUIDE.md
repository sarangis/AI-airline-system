"""
Quick start guide for using the conversational API
"""

# Save this as API_USAGE_GUIDE.md

# Conversational API Quick Start Guide

## Starting a Conversation

### 1. Get Greeting
```bash
curl http://localhost:8000/greeting
```

### 2. Send First Query (New Session)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me flights from delhi to mumbai tomorrow",
    "user_name": "John"
  }'
```

**Save the `session_id` from response for future queries**

### 3. Continue Conversation (Same Session)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "which one is the cheapest?",
    "session_id": "your-session-id-here"
  }'
```

## Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"

class AirlineSupport:
    def __init__(self):
        self.session_id = None
        self.user_name = None
    
    def start_conversation(self, user_name: str):
        """Start a new conversation"""
        self.user_name = user_name
        response = requests.get(f"{BASE_URL}/greeting")
        greeting = response.json()["greeting"]
        print(f"🤖 Assistant: {greeting}\n")
    
    def send_query(self, query: str):
        """Send a query"""
        payload = {
            "query": query,
            "session_id": self.session_id,
            "user_name": self.user_name
        }
        
        response = requests.post(f"{BASE_URL}/query", json=payload)
        data = response.json()
        
        # Store session ID from first response
        if not self.session_id:
            self.session_id = data["session_id"]
        
        print(f"👤 You: {query}\n")
        print(f"🤖 Assistant: {data['message']}\n")
        
        if data.get("follow_up_suggestion"):
            print(f"💡 Hint: {data['follow_up_suggestion']}\n")
    
    def end_session(self):
        """End the conversation"""
        if self.session_id:
            requests.delete(f"{BASE_URL}/session/{self.session_id}")
            print(f"✅ Session ended")

# Usage
if __name__ == "__main__":
    support = AirlineSupport()
    support.start_conversation("John")
    
    support.send_query("show me flights from delhi to mumbai tomorrow")
    support.send_query("which one is the cheapest?")
    support.send_query("book the cheapest flight for me")
    
    support.end_session()
```

## JavaScript/React Example

```javascript
const API_BASE = 'http://localhost:8000';

class AirlineSupportChat {
  constructor() {
    this.sessionId = null;
  }

  async getGreeting() {
    const response = await fetch(`${API_BASE}/greeting`);
    const data = await response.json();
    return data.greeting;
  }

  async sendQuery(query, userName = null) {
    const payload = {
      query,
      session_id: this.sessionId,
      user_name: userName
    };

    const response = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    
    // Store session ID from first response
    if (!this.sessionId) {
      this.sessionId = data.session_id;
    }

    return {
      message: data.message,
      sessionId: data.session_id,
      followUp: data.follow_up_suggestion,
      timestamp: data.timestamp
    };
  }

  async endSession() {
    if (this.sessionId) {
      await fetch(`${API_BASE}/session/${this.sessionId}`, {
        method: 'DELETE'
      });
    }
  }
}

// Usage
const chat = new AirlineSupportChat();
const greeting = await chat.getGreeting();
console.log(greeting);

const response = await chat.sendQuery(
  'Show me flights from delhi to mumbai',
  'John'
);
console.log(response.message);
```

## Common Conversation Flows

### Flow 1: Flight Search & Booking
```
1. Get Greeting
2. User: "show me flights to goa"
3. System: Returns flights with options
4. User: "which is cheapest?"
5. System: Highlights lowest price option
6. User: "book it"
7. System: Confirms booking with reference
8. User: "done"
9. System: Generates session summary
```

### Flow 2: Issue Resolution
```
1. Get Greeting
2. User: "my flight was cancelled"
3. System: Asks for booking reference
4. User: "AI2024001"
5. System: Retrieves booking, offers rebooking
6. User: "any flights tomorrow?"
7. System: Shows alternatives
8. User: "rebook me on AI401"
9. System: Confirms new booking
```

### Flow 3: FAQ Queries
```
1. Get Greeting
2. User: "what's your baggage policy?"
3. System: Provides policy information
4. User: "can i carry a laptop?"
5. System: Clarifies baggage details
6. User: "thanks!"
7. System: Offers further help
```

## Session Information

Check session details anytime:
```bash
curl http://localhost:8000/session/your-session-id
```

Returns:
```json
{
  "session_id": "abc-123-def",
  "message_count": 5,
  "user_name": "John",
  "booking_ref": "AI2024001",
  "session_start": "2024-06-28T10:00:00"
}
```

## Tips for Best Results

1. **Be Specific** - More details = better responses
   - ❌ "show me flights"
   - ✅ "show me flights from delhi to mumbai tomorrow morning"

2. **Use Natural Language** - System handles misspellings
   - ❌ "flites from delh to bom"
   - ✅ "flights from delhi to mumbai"

3. **Provide Context** - Include booking references when relevant
   - ✅ "I want to change my booking AI2024001"

4. **One Query at a Time** - Sequential queries = better responses
   - ❌ "show flights and book one for me"
   - ✅ First: "show flights from delhi to mumbai"
   - ✅ Then: "book the 6am flight"

5. **Clarify When Asked** - System may ask follow-up questions
   - System: "Do you have a preferred airline?"
   - ✅ "yes, air india" or "no preference"

## Error Handling

```python
try:
    response = requests.post(f"{API_BASE}/query", json=payload)
    data = response.json()
    
    if response.status_code == 200:
        print(data['message'])
    else:
        print(f"Error: {data.get('detail', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
```

## Rate Limiting

Current implementation has no rate limiting. For production:
- Add rate limiting per session_id
- Implement request queuing
- Add timeout handling

## Session Persistence

Current: In-memory (sessions lost on restart)
Future: Add database persistence:
```python
# Using MongoDB
db.conversations.insert_one({
    "session_id": session_id,
    "user_id": user_id,
    "messages": [...],
    "created_at": datetime.now(),
    "last_activity": datetime.now()
})
```

## Troubleshooting

### Session Not Found
```
Status: 404
Solution: Create new session (don't include session_id)
```

### API Not Responding
```
Check if FastAPI server is running:
$ curl http://localhost:8000/health
```

### Slow Responses
```
LLM calls take 1-3 seconds
- Normal latency: 1-3 seconds per response
- If longer: Check API key quota or LLM service status
```

## Advanced: Custom Conversation Middleware

```python
from functools import wraps

def log_conversation(func):
    """Decorator to log all conversations"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = args[0] if args else None
        result = await func(*args, **kwargs)
        
        # Log to file or database
        with open("conversations.log", "a") as f:
            f.write(f"{result['session_id']}: {request.query}\n")
        
        return result
    return wrapper

@app.post("/query")
@log_conversation
async def process_query(request: QueryRequest):
    # ... rest of implementation
```

## Support

For issues or questions:
- Check CONVERSATIONAL_MESSAGING.md for detailed documentation
- Run test_conversation.py to verify setup
- Check API logs for error details
