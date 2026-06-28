# Conversational Messaging System

## Overview
Added a complete conversational messaging system that makes the airline support chatbot more interactive, friendly, and context-aware. The system maintains conversation history, understands context, and generates natural, human-like responses.

## Key Features

### 1. **Conversation History Management**
Tracks multi-turn conversations with full context:

```python
conversation = ConversationHistory()
conversation.user_name = "John"
conversation.booking_ref = "AI2024001"

conversation.add_message("user", "show me flights from delhi")
conversation.add_message("assistant", "Here are the flights...")

# Access context for LLM
context = conversation.get_conversation_context()
```

### 2. **Conversational Response Formatting**
Converts technical responses to natural language:

```
Technical: [{"flight": "AI101", "time": "06:00", "price": 3500}, ...]
Conversational: "Here are the available flights! I found 3 great options for you:
- AI101 departing at 6:00 AM for ₹3,500
- AI201 departing at 12:00 PM for ₹4,000
- AI301 departing at 6:00 PM for ₹3,800

Which one interests you?"
```

### 3. **Personalized Greetings**
Generates friendly, context-aware opening messages:

```
"Hello! I'm your airline support assistant. How can I help you today?"
"Good evening! Welcome to airline support. What can I assist you with?"
```

### 4. **Clarification Questions**
Asks smart follow-up questions when queries are ambiguous:

```
User: "I want to change my flight"
System: "I'd be happy to help! To process your change request, could you please provide:
1. Your current booking reference?
2. Which flight segment would you like to change?
3. Do you have specific date/time preferences?"
```

### 5. **Session-Based Conversations**
Each user gets a unique session with full history tracking:

- Session ID for identification
- User profile information
- Booking references
- Complete message history
- Timestamp tracking

### 6. **Session Summaries**
Automatically summarizes conversations:

```
"During this session, the user inquired about flights from Delhi to Mumbai 
and successfully booked AI401 for tomorrow morning. No outstanding issues remain."
```

## API Endpoints

### 1. **POST /query** (Main endpoint)
Process a query with conversational response:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me flights from delhi to mumbai tomorrow",
    "session_id": "optional-uuid",
    "user_name": "John",
    "booking_ref": "AI2024001"
  }'
```

**Response:**
```json
{
  "message": "Great! I found several flights for you tomorrow from Delhi to Mumbai...",
  "original_response": "[technical data]",
  "session_id": "abc-123-def",
  "timestamp": "2024-06-28T10:30:00",
  "follow_up_suggestion": "Would you like to book one of these flights?"
}
```

### 2. **POST /chat** (Alias for /query)
Same as /query, just a different endpoint name for convenience:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "help me book a flight"}'
```

### 3. **GET /greeting**
Get an initial greeting:

```bash
curl "http://localhost:8000/greeting"
```

**Response:**
```json
{
  "greeting": "Hello! I'm your airline support assistant. How can I help you today?",
  "session_hint": "Use the /query endpoint with your first query"
}
```

### 4. **POST /clarify**
Get clarifying questions for ambiguous queries:

```bash
curl -X POST "http://localhost:8000/clarify" \
  -H "Content-Type: application/json" \
  -d '{"query": "i want to change my flight"}'
```

**Response:**
```json
{
  "clarifications": "To help you change your flight, I need to know:...",
  "original_query": "i want to change my flight"
}
```

### 5. **GET /session/{session_id}**
Get conversation session information:

```bash
curl "http://localhost:8000/session/abc-123-def"
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "message_count": 5,
  "user_name": "John",
  "booking_ref": "AI2024001",
  "session_start": "2024-06-28T10:00:00"
}
```

### 6. **DELETE /session/{session_id}**
Clear/end a conversation session:

```bash
curl -X DELETE "http://localhost:8000/session/abc-123-def"
```

**Response:**
```json
{
  "status": "success",
  "message": "Session cleared"
}
```

### 7. **GET /health**
Check API health and active sessions:

```bash
curl "http://localhost:8000/health"
```

## Multi-Turn Conversation Example

### Session Start
```
User: "Hi, I need help with flights to Goa"
API: POST /query with session_id=null
Response: Creates new session, returns conversational greeting + offers help
```

### Conversation Continue
```
User: "Show me flights for next week"
API: POST /query with session_id="abc-123" (from previous response)
Response: Uses conversation history for context, provides relevant flights
```

### More Context
```
User: "Can I book the cheapest one?"
API: POST /query with same session_id
Response: Recalls previous flights, books the ₹2500 option, generates booking confirmation
```

### Session End
```
User: "Thanks, that's all!"
API: DELETE /session/abc-123
Response: Clears session
```

## Architecture

```
User Input
    ↓
Parse Request (Query, Session ID, User Info)
    ↓
Get or Create Session
    ↓
Add to Conversation History
    ↓
Process Query (Core Logic)
    ↓
Get Technical Response
    ↓
Format Response Conversationally
    ↓
Add Response to History
    ↓
Generate Follow-up Suggestion
    ↓
Return Conversational Response
```

## Components

### ConversationHistory Class
Manages conversation state and history:

```python
conversation = ConversationHistory(max_history=10)
conversation.user_name = "John"
conversation.booking_ref = "AI2024001"

conversation.add_message("user", "query text")
conversation.add_message("assistant", "response text")

# Access methods
context = conversation.get_conversation_context()  # For LLM context
last_query = conversation.get_last_user_query()    # Get last query
session_dict = conversation.to_dict()              # Full session dict
conversation.clear()                               # Reset session
```

### Conversation Formatters
- **create_conversational_response_formatter()** - Converts technical responses to natural language
- **create_greeting_generator()** - Generates personalized greetings
- **create_clarification_asker()** - Asks clarifying questions
- **create_session_summarizer()** - Summarizes conversations

### Response Building
```python
response = build_conversational_response(
    technical_response="[sql result]",
    user_query="show me flights",
    conversation_history=conversation,
    response_formatter=formatter,
    query_metadata={"query_type": "flight_search"}
)
```

## Conversation Flow

1. **User Sends Query**
   - Include session_id (or null for new session)
   - Include user_name, booking_ref (optional)

2. **System Creates/Retrieves Session**
   - New sessions get unique UUID
   - Existing sessions are retrieved from memory

3. **Query is Processed**
   - Spell correction applied
   - Core logic processes query
   - Technical response generated

4. **Response is Formatted**
   - Uses conversation history for context
   - Converts technical data to natural language
   - Adds personalization and warmth
   - Generates follow-up suggestions

5. **Conversation History Updated**
   - Both user query and assistant response stored
   - Metadata captured (timestamps, query type, etc.)
   - Session info maintained

6. **Response Returned to User**
   - Conversational message
   - Session ID for continuity
   - Follow-up suggestions
   - Original technical response (for debugging)

## Session Management

### Storing Sessions
Currently uses in-memory dictionary:
```python
conversations: Dict[str, ConversationHistory] = {}
```

### Future: Database Storage
```python
# Store in database for persistence
db.sessions.insert({
    "session_id": "abc-123",
    "messages": [...],
    "user_info": {...},
    "created_at": timestamp,
    "last_activity": timestamp
})
```

## Testing

Run the conversational features test:
```bash
python test_conversation.py
```

Tests:
1. Greeting generation
2. Conversation history management
3. Response formatting
4. Clarification questions
5. Complete conversation flows
6. Session summaries
7. Session information tracking

## Example Conversation

```
👤 User: hi, can you help me find flights?

🤖 Assistant: Of course! I'd be happy to help you find flights. 
To get you the best options, could you tell me:
- Where are you flying from?
- Where would you like to go?
- What date are you looking to travel?

👤 User: from delhi to mumbai tomorrow

🤖 Assistant: Great! I found 5 wonderful flights for you from Delhi to Mumbai tomorrow. 
Here are some options ranging from ₹2,500 to ₹5,000. The most popular is AI401 
departing at 6:00 AM for ₹3,500. Would you like more details about any of these flights?

👤 User: show me all options

🤖 Assistant: Perfect! Here are all the available flights:
1. AI401 - 6:00 AM to 8:00 AM - ₹3,500
2. AI201 - 9:00 AM to 11:00 AM - ₹4,000
3. AI301 - 12:00 PM to 2:00 PM - ₹3,800
4. AI501 - 3:00 PM to 5:00 PM - ₹4,200
5. AI601 - 6:00 PM to 8:00 PM - ₹5,000

Would you like to book one of these flights?
```

## Configuration

### Adjust Response Temperature
In `api/main.py`:
```python
llm = ChatOpenAI(
    temperature=0.5,  # 0 = formal, 0.7 = creative, 1 = random
    ...
)
```

### Adjust Session History Size
In `conversation_manager.py`:
```python
conversation = ConversationHistory(max_history=20)  # Keep more messages
```

## Benefits

✅ **Context-Aware** - Remembers previous interactions
✅ **Natural** - Converts technical responses to human language
✅ **Personalized** - Uses user names and booking references
✅ **Multi-Turn** - Maintains full conversation history
✅ **Helpful** - Asks clarifying questions when needed
✅ **Summarizable** - Can summarize entire sessions
✅ **Extensible** - Easy to add new conversation features
✅ **Persistent** - Session tracking across multiple queries

## Files Modified/Created

- **Created**: `src/conversation_manager.py` - Conversation management
- **Modified**: `api/main.py` - Added conversation endpoints
- **Created**: `test_conversation.py` - Test suite for conversations
