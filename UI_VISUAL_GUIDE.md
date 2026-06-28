# Streamlit UI Visual Guide - Plus Button & Session Management

## 🎨 Main UI Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ✈️ AI Airline Support           [➕ New Session]  [🔄 Refresh]             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📍 Session: abc-123-def...  |  👤 Your Name: [___________]  |  💬 Msgs: 5 │
│                                                                              │
├────────────────────────────┬──────────────────────────────────────────────────┤
│       SIDEBAR              │              MAIN CHAT AREA                     │
│                            │                                                  │
│  📋 SESSION MANAGEMENT     │  📝 CONVERSATION HISTORY                        │
│  ────────────────────────  │  ──────────────────────────                     │
│                            │  User: Show flights from delhi                  │
│  Previous Sessions:        │  Assistant: 👋 Here are flights...             │
│  ┌──────────────────────┐  │  User: What's the cheapest?                    │
│  │ John - 5 msgs       │  │  Assistant: Based on price, SG820...            │
│  │ Priya - 3 msgs      │  │  User: Can I book that?                         │
│  │ Rajesh - 7 msgs     │  │  Assistant: Yes! Here's how...                  │
│  │ Admin - 2 msgs      │  │                                                  │
│  └──────────────────────┘  │                                                  │
│                            │                                                  │
│  [📂 Resume Session]       │  💬 YOUR MESSAGE                                │
│                            │  ────────────────────────────────────            │
│  ────────────────────────  │  [Enter message here            ] [Send ➤]     │
│                            │                                                  │
│  🔍 SEARCH SESSIONS        │                                                  │
│  ────────────────────────  │                                                  │
│  [Search box: "delhi"   ]  │                                                  │
│                            │                                                  │
│  Results: 2 sessions       │                                                  │
│  ┌──────────────────────┐  │                                                  │
│  │ 👤 Alice             │  │                                                  │
│  │ Topics: delhi, flight│  │                                                  │
│  │        [Load]        │  │                                                  │
│  └──────────────────────┘  │                                                  │
│  ┌──────────────────────┐  │                                                  │
│  │ 👤 Bob               │  │                                                  │
│  │ Topics: delhi, refund│  │                                                  │
│  │        [Load]        │  │                                                  │
│  └──────────────────────┘  │                                                  │
│                            │                                                  │
└────────────────────────────┴──────────────────────────────────────────────────┘
```

## 📍 Plus Button Location

```
┌─ Page Header ────────────────────────────────────────────────┐
│                                                              │
│  ✈️ AI Airline Support              [➕]  [🔄]             │  ← PLUS BUTTON
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 🔄 User Interaction Flow

### New Session Flow
```
User Action:
┌─────────────────┐
│ Click ➕ Button │
└────────┬────────┘
         │
         ↓
┌─────────────────────────┐
│ ✅ New session started! │
└────────┬────────────────┘
         │
         ↓
┌──────────────────────────┐
│ Session ID: xyz-123...   │
│ Messages: 0              │
└────────┬─────────────────┘
         │
         ↓
┌─────────────────────┐
│ Ready for new chat  │
└─────────────────────┘
```

### Resume Session Flow
```
User Action:
┌──────────────────────────┐
│ Select from dropdown     │
│ Click 📂 Resume Session  │
└────────┬─────────────────┘
         │
         ↓
┌───────────────────────┐
│ Loading from storage  │
└────────┬──────────────┘
         │
         ↓
┌──────────────────────────────────┐
│ "Welcome back! We last discussed │
│ flights to goa. How can I help?" │
└────────┬─────────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│ Full conversation history   │
│ loaded (5 messages visible) │
└────────┬─────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│ Ready to continue (same      │
│ context, AI remembers all)   │
└──────────────────────────────┘
```

## 🎯 Component Breakdown

### 1. Top Navigation Bar
```
[Logo] [Title]                    [➕ New] [🔄 Refresh]
                                   ↑        ↑
                          New Session    Reload Page
```

### 2. Session Info Panel
```
📍 Session ID: abc-123...
   Shows current session identifier

👤 Your Name: [Input Field]
   Optional: Enter name for personalization

💬 Messages: 5
   Count of messages in current session
```

### 3. Left Sidebar - Session Management
```
┌─ SECTION 1: Previous Sessions ─┐
│ Dropdown with up to 10 sessions│
│ Shows: User, msg count, summary│
│ Button: Resume                 │
└────────────────────────────────┘

┌─ SECTION 2: Search Sessions ───┐
│ Search box for keyword         │
│ Shows results with Load button │
│ Results limited to top 5       │
└────────────────────────────────┘
```

### 4. Main Chat Area
```
┌─ Conversation History ─────┐
│ Displays all messages:     │
│ - User messages (right)    │
│ - Assistant responses(left)│
│ - Full history visible    │
└────────────────────────────┘

┌─ Message Input ────────────┐
│ [Text input field] [Send] │
│ Enter query & click Send  │
│ Auto-saves after send     │
└────────────────────────────┘
```

## 🎨 Button Styles

### Plus Button (New Session)
```
┌─────────────────┐
│  ➕ New Session │
│   Green/Primary │
│   Prominent     │
└─────────────────┘
```

### Refresh Button
```
┌──────────┐
│  🔄      │
│ Secondary│
└──────────┘
```

### Resume Button
```
┌──────────────────┐
│  📂 Resume      │
│  Secondary      │
│  In Sidebar     │
└──────────────────┘
```

### Send Button
```
┌──────────┐
│ Send ➤  │
│ Primary │
└──────────┘
```

## 📊 State Display Examples

### New Session Started
```
✅ New session started!

Session Info:
📍 Session: f0653a2b-1cc3-4567-9888-fc9f784d8e05
👤 Your Name: Alice
💬 Messages: 0

Ready for input
```

### Active Conversation
```
Session Info:
📍 Session: f0653a2b-1cc3-4567-9888-fc9f784d8e05
👤 Your Name: Alice
💬 Messages: 4

Conversation shown with
all 4 messages visible
```

### Resumed Session
```
✅ Resumed session

"Welcome back, Alice! I see we last talked about
flights to Delhi. How can I assist you today?"

Full history loaded (5 messages visible)
Session ID: same as before
Ready to continue
```

## 🔍 Search Results Display

### Search in Progress
```
🔍 SEARCH SESSIONS
─────────────────
[Search: "delhi" ]

Searching...
```

### Search Results
```
Found 2 sessions with "delhi"

┌─ Result 1 ─────────────────┐
│ 👤 Alice                   │
│ Topics: delhi, flights     │
│ Date: 2024-06-28          │
│ [Load]                     │
└────────────────────────────┘

┌─ Result 2 ─────────────────┐
│ 👤 Bob                     │
│ Topics: delhi, refund      │
│ Date: 2024-06-27          │
│ [Load]                     │
└────────────────────────────┘
```

## 💬 Message Display Format

### User Message
```
┌────────────────────────────────────┐
│ User: Show flights from delhi      │
│       to mumbai tomorrow           │
└────────────────────────────────────┘
   ↑
   Right-aligned
   Blue/Light background
```

### Assistant Message
```
┌────────────────────────────────────┐
│ Assistant: Here are the flights    │
│            from Delhi to Mumbai:   │
│            ...                     │
└────────────────────────────────────┘
   ↑
   Left-aligned
   Gray/Light background
```

## ✨ Status Indicators

### Success
```
✅ New session started!
✅ Resumed session
✅ Session loaded!
```

### Processing
```
🤖 Thinking...
Loading...
```

### Warnings
```
⚠️ Please enter a message
⚠️ No sessions found
```

### Errors
```
❌ Cannot connect to API
❌ Error creating session
❌ Session not found
```

## 📱 Responsive Design

### Desktop View (1200px+)
```
Wide layout with sidebar always visible
Full conversation history display
Easy access to all controls
```

### Tablet View (768px-1199px)
```
Sidebar can collapse/expand
Smaller conversation display
Touch-friendly buttons
```

### Mobile View (<768px)
```
Sidebar moves to top
Stacked layout
Large touch targets
Conversation auto-scrolls
```

## 🎯 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| R | Refresh page |
| Tab | Navigate between inputs |
| Enter | Send message (in input field) |
| Esc | Clear search |

## 🌈 Color Scheme

| Element | Color | Usage |
|---------|-------|-------|
| Plus Button | Green | Primary action |
| Refresh Button | Blue | Secondary action |
| User Message | Light Blue | User input |
| Assistant Message | Light Gray | AI response |
| Success | Green | ✅ confirmation |
| Error | Red | ❌ problems |
| Warning | Yellow | ⚠️ caution |

## 🎬 Animation Effects

### Button Hover
```
Plus button → Slight scale increase
Color slightly brighter
Cursor changes to pointer
```

### Message Appear
```
New messages fade in
Slight slide animation
Auto-scroll to bottom
```

### Loading State
```
Spinner animation
"Thinking..." indicator
Message appears when done
```

## 🔔 User Notifications

### Inline Messages
```
✅ Success messages in green
⚠️ Warnings in yellow
❌ Errors in red
```

### Toast-style (if added in future)
```
Brief notification at top
Auto-disappears after 3 seconds
Non-intrusive
```

## 📊 Metrics Display

### Session Panel
```
Session Count:
- 📍 Current Session ID (truncated)
- 👤 User Name (editable)
- 💬 Message Count (auto-updating)
```

### Sidebar Stats (if added)
```
📈 Total Sessions: 42
📝 Total Messages: 156
👥 Unique Users: 8
💾 Storage: 2.3 MB
```

## 🚀 Performance Indicators

### Fast Operations
```
New Session: Instant ✅
Send Message: 2-5 seconds
Resume: <1 second
Search: <1 second
```

### Data Sync
```
Auto-save: After each message
Sync Status: ✅ All saved
Last saved: 30 seconds ago
```

## 🎓 User Guidance

### Tooltips (on hover)
```
[➕ New Session] → "Start a fresh conversation"
[🔄 Refresh] → "Reload the current session"
[📂 Resume] → "Load this conversation"
[Send ➤] → "Send your message"
```

### Help Messages
```
"🚀 Click '➕ New Session' to start a conversation"
"📂 Select a session and click 'Resume' to continue"
"🔍 Search for past conversations in the sidebar"
```

---

## 📖 Quick Reference

### Most Common Actions

1. **Start New Chat**
   - Click ➕ in top-right
   - Type message
   - Click Send

2. **Continue Old Chat**
   - Select from sidebar dropdown
   - Click 📂 Resume
   - Continue typing

3. **Find Old Chat**
   - Type in Search box
   - Click Load on result
   - Chat opens

4. **Switch Topics**
   - Click ➕ anytime
   - Starts fresh conversation
   - All old ones still saved

---

**Visual Guide Version**: 1.0  
**Last Updated**: June 28, 2024  
**Status**: Complete & Live ✅
