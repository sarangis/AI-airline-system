# Quick Start: New Session UI with Plus Button

## What's New ✨

The Streamlit UI now has full session management with a **plus button (➕)** to start new conversations!

## Access the UI

```
http://localhost:8501
```

## Key Features

### 1. Plus Button (➕) - Top Right
**Click to start a brand new conversation**

```
┌─────────────────────────────────────────┐
│  ✈️ AI Airline Support  [➕ New]  [🔄] │
└─────────────────────────────────────────┘
```

- Clears all previous context
- Creates new session ID
- Perfect for switching topics

### 2. Session Info Panel
**Shows your current session**

```
📍 Session ID: abc-123...  |  👤 Name: [input]  |  💬 Messages: 5
```

- See your session ID
- Enter your name (optional)
- Track message count

### 3. Left Sidebar - Session Management
**Resume old conversations**

```
📋 SESSION MANAGEMENT
━━━━━━━━━━━━━━━━━━━━
📂 Previous Sessions
[Select from list]
[📂 Resume Session]

🔍 SEARCH SESSIONS
[Search box]
[Results]
```

### 4. Chat Interface - Main Area
**Send and view messages**

```
📝 CONVERSATION HISTORY
─────────────────────
User: Show flights from Delhi
Assistant: Here are the flights...
User: Book the cheapest
Assistant: I'll help you book...

💬 YOUR MESSAGE
[Message input box] [Send ➤]
```

## Common Tasks

### Task 1: Start a New Conversation
```
1. Click ➕ New Session (top right)
2. Enter your name (optional)
3. Type your message
4. Click Send ➤
5. See response
6. Continue chatting
```

### Task 2: Resume a Previous Chat
```
1. Look at left sidebar
2. Select session from dropdown
3. Click 📂 Resume Session
4. See welcome message
5. Full conversation history loads
6. Continue chatting
```

### Task 3: Search for Old Conversation
```
1. Go to left sidebar
2. Type keyword: "delhi" or "booking"
3. See matching sessions
4. Click [Load] on result
5. Session opens with full history
```

### Task 4: Check Session Statistics
```
1. Scroll down in sidebar
2. Look for Stats section (if visible)
3. See total sessions and messages
```

## UI Buttons Explained

| Button | Icon | Action |
|--------|------|--------|
| New Session | ➕ | Start fresh conversation |
| Refresh | 🔄 | Reload current session |
| Resume | 📂 | Load old session |
| Send | ➤ | Send your message |
| Load | 📂 | Open search result |

## Example Flow

### Scenario 1: Check Flight Status → Book Flight
```
Step 1:
- Click ➕ New Session
- Type: "What flights are available from Delhi?"
- Send ➤

Step 2:
- Continue in same session
- Type: "Book flight 6E477"
- Send ➤

Step 3 (Later, after closing browser):
- Open http://localhost:8501
- Select session from sidebar
- Click 📂 Resume Session
- Full history appears!
- Type: "What's my booking reference?"
- AI remembers the booking
```

### Scenario 2: Multiple Different Topics
```
Session A (Flights):
- Click ➕ New Session
- Chat about flights
- Auto-saved

Session B (Refund):
- Click ➕ New Session
- Chat about refunds
- Auto-saved (separate session)

Switch back:
- Select Session A from sidebar
- Click 📂 Resume Session
- Back to flights conversation
```

## Status Indicators

| Status | Meaning |
|--------|---------|
| ✅ | Success - action completed |
| 🤖 | Thinking - API processing |
| ⚠️ | Warning - attention needed |
| ❌ | Error - something went wrong |

## Tips & Tricks

1. **Save Session IDs** - Copy from the Session ID display if you need to share
2. **Use Your Name** - Personalized responses work better
3. **Related Topics = Same Session** - Keep related questions together
4. **Search Before Asking** - Your answer might be in an old session
5. **Switch Topics** - Click ➕ to separate unrelated conversations

## Keyboard Shortcuts

- `R` - Refresh the page (Streamlit shortcut)
- `Ctrl+Enter` - Send message (in some text fields)

## Mobile Support

✅ Works on mobile browsers
- Sidebar moves to top
- Touch-friendly buttons
- Same functionality

## Data Persistence

✅ **Auto-Save**: Every message is automatically saved
✅ **Survive Restart**: Close browser, open again - messages still there
✅ **Server Restart**: Restart API - sessions still there

## What Gets Saved

- ✅ All your messages
- ✅ All AI responses
- ✅ Your name
- ✅ Conversation timestamp
- ✅ Session summary

## Troubleshooting

### "Cannot connect to API"
→ Make sure FastAPI is running on port 8000

### "Session not loading"
→ Click 🔄 Refresh button or press R

### "Can't find old session"
→ Use 🔍 Search Sessions in sidebar

### "Messages disappeared"
→ Check if you clicked ➕ New Session by mistake

## API Info

| Endpoint | Used For |
|----------|----------|
| POST /new-session | Create new session |
| POST /query | Send message |
| GET /sessions | List sessions |
| POST /resume-session | Load old session |
| GET /search-sessions | Search |

## Performance

- New session: Instant
- Send message: 2-5 seconds
- Resume session: < 1 second
- Search: < 1 second

## Storage Location

All conversations saved in:
```
data/conversations/
├── index.json (metadata)
└── session-*.json (data)
```

## Security Note

⚠️ This is a single-user application. No authentication or multi-user support.

## Getting Help

### Check UI Guide
```
Read: STREAMLIT_UI_GUIDE.md
```

### Check Implementation Details
```
Read: UI_SESSIONS_IMPLEMENTATION.md
```

### Check Session API Guide
```
Read: PERSISTENT_SESSIONS_QUICK_REF.md
```

## Next Steps

1. ✅ Open UI: http://localhost:8501
2. ✅ Click ➕ New Session
3. ✅ Type a question about flights
4. ✅ Click Send ➤
5. ✅ See conversation history
6. ✅ Ask follow-up questions
7. ✅ Click ➕ to start new topic
8. ✅ Resume old sessions from sidebar

---

**All features are LIVE and ready to use!** 🚀

For detailed docs, see: `STREAMLIT_UI_GUIDE.md` and `UI_SESSIONS_IMPLEMENTATION.md`
