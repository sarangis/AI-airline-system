# Streamlit UI - Session Management Guide

## Overview
Enhanced Streamlit UI with session management features:
- ➕ New Session button
- 📋 Conversation history display
- 📂 Resume previous sessions
- 🔍 Search past conversations
- 💬 Chat interface with context

## UI Components

### Top Bar
```
[Title] [➕ New Session] [🔄 Refresh]
```

- **Title**: Application name
- **➕ New Session**: Start a completely fresh conversation
- **🔄 Refresh**: Refresh the current session

### Session Information Panel
```
📍 Session ID: abc-123...  | 👤 Your Name: [text box] | 💬 Messages: 5
```

Shows:
- Current session ID (truncated)
- User name input field
- Message count in current session

### Sidebar: Session Management
```
📋 SESSION MANAGEMENT
────────────────────
📂 Previous Sessions
[Select dropdown]
[📂 Resume Session]

────────────────────
🔍 SEARCH SESSIONS
[Search box]
[Results list with Load buttons]
```

### Main Chat Area
```
📝 CONVERSATION HISTORY
User: [message]
Assistant: [response]
User: [message]
Assistant: [response]

💬 YOUR MESSAGE
[Message input box] [Send ➤]
```

## Features

### 1. New Session (➕ Button)
**Purpose**: Start a completely new conversation
**Action**: 
- Clears conversation history
- Creates new session ID
- Resets context

**When to use**:
- Starting a new topic
- Different issue/booking
- Want fresh context

```
Click ➕ New Session
    ↓
✅ New session started!
    ↓
Enter your message
```

### 2. Resume Previous Session (📂 Button)
**Purpose**: Continue an old conversation
**Action**:
- Loads previous session with full history
- Shows welcome back message
- Uses complete context

**When to use**:
- Continuing from where you left off
- Asking follow-up questions
- Related to previous booking

```
Select from dropdown
    ↓
Click 📂 Resume Session
    ↓
✅ Resumed session
    ↓
Full history visible
```

### 3. Search Sessions (🔍)
**Purpose**: Find past conversations
**Search by**:
- Keyword in conversation
- User name
- Booking reference
- Topics discussed

**Results**: Shows matching sessions with Load button

```
Type keyword: "delhi"
    ↓
View results
    ↓
Click Load
    ↓
Session loaded
```

### 4. Conversation History (📝)
**Shows**:
- All messages in current session
- User messages (right-aligned)
- Assistant responses (left-aligned)
- Full context preserved

### 5. Your Name (👤)
**Purpose**: Personalization
**Usage**:
- Enter your name
- Used for greetings
- Helps identify sessions

## User Workflows

### Workflow 1: New Conversation
```
1. Click ➕ New Session
2. Enter your name (optional)
3. Type your query
4. Click Send ➤
5. View response
6. Continue chatting or click ➕ New Session to switch topics
```

### Workflow 2: Resume Old Conversation
```
1. Look at sidebar
2. Select from "Previous Sessions" dropdown
3. Click 📂 Resume Session
4. See welcome back message
5. Continue where you left off
6. Full history available for context
```

### Workflow 3: Search for Specific Conversation
```
1. Go to sidebar
2. Type keyword in search box (e.g., "flight to goa")
3. View search results
4. Click Load on matching session
5. Session opens with full history
```

### Workflow 4: Multiple Sessions
```
Session 1 (Flight Booking):
- Click ➕ New Session
- Chat about flights
- [Auto-saved]

Later, new topic (Refund):
- Click ➕ New Session
- Chat about refund
- [Auto-saved separately]

Can resume both anytime!
```

## Keyboard Shortcuts & Tips

### Streamlit Tips
- Press `R` to refresh the page
- Click anywhere to interact
- Messages auto-save (no manual save needed)

### Best Practices
1. **Use descriptive queries**: More specific = better responses
2. **Keep related topics together**: Use same session for related questions
3. **Use names**: Enter your name for better personalization
4. **Search before asking**: Might find answer in old session
5. **Start fresh when needed**: Use ➕ for unrelated topics

## Status Indicators

### Messages
- ✅ Success messages (green)
- ⚠️ Warnings (yellow)
- ❌ Errors (red)
- 🤖 Thinking (while processing)

### Session States
- `📍 Session ID`: Current session active
- `💬 Messages: X`: Number of messages in session
- `✅ New session started`: Just created
- `✅ Resumed session`: Loaded from storage
- `✅ Session loaded!`: Resumed from search

## Session Display

### Previous Sessions List
Shows up to 10 most recent sessions with:
- **User name**: Who started it
- **Message count**: How many messages
- **Summary**: Topics discussed
- **Selection button**: To resume

Example:
```
👤 John - 5 msgs - Topics discussed: flight, booking
👤 Priya - 3 msgs - Topics discussed: refund
👤 Rajesh - 7 msgs - Topics discussed: delay, rebooking
```

### Search Results
Shows matching sessions with:
- User name
- Summary of topics
- Load button to open

Example:
```
🔍 Search results for "delhi": 3 session(s)

👤 John - Topics discussed: flight, delhi
  [Load]

👤 Priya - Topics discussed: delhi, booking
  [Load]

👤 Admin - Topics discussed: delhi, airport
  [Load]
```

## Troubleshooting

### Issue: "Cannot connect to API"
```
Solution: Check if FastAPI is running
Command: uvicorn api/main:app --host 0.0.0.0 --port 8000
```

### Issue: Session not loading
```
Solution 1: Refresh the page (Press R)
Solution 2: Click 🔄 Refresh button
Solution 3: Try another session
```

### Issue: Messages not appearing
```
Solution: Click 🔄 Refresh or press R
This reloads the conversation history
```

### Issue: Can't find old session
```
Solution: Use 🔍 Search Sessions
Search by keyword, user name, or topic
```

## Session Information

### Current Session Display
```
📍 Session ID: abc-123-def-456...
👤 Your Name: [Empty or your name]
💬 Messages: 5
```

### Session Metadata
- **Session ID**: Unique identifier
- **User Name**: Personal identification
- **Message Count**: Total messages in session
- **Summary**: Topics discussed
- **Last Updated**: When session was last used

## API Integration

### Endpoints Used
- `POST /new-session` - Start new session
- `POST /query` - Send message
- `GET /sessions` - List all sessions
- `POST /resume-session/{id}` - Resume session
- `GET /search-sessions` - Search sessions

### Automatic Features
- ✅ Auto-save after each message
- ✅ Auto-load session history
- ✅ Auto-generate welcome messages
- ✅ Auto-provide context to AI

## UI Customization (Advanced)

### Change layout
```python
# In streamlit_app.py
st.set_page_config(layout="wide")  # or "centered"
```

### Change colors/theme
```python
# Streamlit uses theme configuration
# In .streamlit/config.toml:
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F0F0F0"
```

### Adjust session limits
```python
# In streamlit_app.py
st.session_state.available_sessions = sessions_data.get("sessions", [])[:20]  # Change 20 to desired limit
```

## Performance Tips

1. **Session limit**: Only shows 20 most recent sessions
2. **Search limit**: Shows top 5 matching results
3. **History**: Automatically truncated to reduce UI lag
4. **Caching**: Previous sessions cached in sidebar

## Security Notes

- Session IDs are displayed (design choice for accessibility)
- User names are optional
- Conversations stored locally in `data/conversations/`
- No authentication required (single user)

## Future Enhancements

- [ ] Export conversation as PDF
- [ ] Delete individual messages
- [ ] Conversation tags/labels
- [ ] Favorites/starred conversations
- [ ] User authentication
- [ ] Multi-user support
- [ ] Message reactions/ratings
- [ ] Conversation templates
