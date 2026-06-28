# ui/streamlit_app.py

import streamlit as st
import requests
import os
from datetime import datetime

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
QUERY_ENDPOINT = f"{API_BASE_URL}/query"
NEW_SESSION_ENDPOINT = f"{API_BASE_URL}/new-session"
SESSIONS_ENDPOINT = f"{API_BASE_URL}/sessions"
RESUME_SESSION_ENDPOINT = f"{API_BASE_URL}/resume-session"
SEARCH_ENDPOINT = f"{API_BASE_URL}/search-sessions"

st.set_page_config(page_title="Airline Customer Support AI", layout="wide")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "available_sessions" not in st.session_state:
    st.session_state.available_sessions = []

# Header with Title and Session Controls
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.title("✈️ AI Airline Support")

with col2:
    if st.button("➕ New Session", key="new_session_btn", use_container_width=True):
        try:
            user_name = st.session_state.user_name or None
            response = requests.post(
                NEW_SESSION_ENDPOINT,
                json={"user_name": user_name}
            )
            response.raise_for_status()
            data = response.json()
            
            st.session_state.session_id = data.get("session_id")
            st.session_state.conversation_history = []
            
            st.success("✅ New session started!")
            st.rerun()
        except Exception as e:
            st.error(f"Error creating new session: {e}")

with col3:
    if st.button("🔄 Refresh", key="refresh_btn", use_container_width=True):
        st.rerun()

st.markdown("---")

# Session Information Panel
if st.session_state.session_id:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📍 Session ID", st.session_state.session_id[:12] + "...")
    
    with col2:
        user_name = st.text_input("👤 Your Name", value=st.session_state.user_name or "", key="user_name_input")
        if user_name != st.session_state.user_name:
            st.session_state.user_name = user_name
    
    with col3:
        st.metric("💬 Messages", len(st.session_state.conversation_history))

# Sidebar: Session Management
with st.sidebar:
    st.header("📋 Session Management")
    
    # Load previous sessions
    try:
        sessions_response = requests.get(f"{SESSIONS_ENDPOINT}?limit=20")
        sessions_response.raise_for_status()
        sessions_data = sessions_response.json()
        st.session_state.available_sessions = sessions_data.get("sessions", [])
    except Exception as e:
        st.warning(f"Could not load sessions: {e}")
    
    if st.session_state.available_sessions:
        st.subheader("Previous Sessions")
        
        # Create session options for dropdown
        session_options = []
        for sess in st.session_state.available_sessions[:10]:  # Show top 10
            user = sess.get("user_name", "Unknown")
            msg_count = sess.get("message_count", 0)
            summary = sess.get("summary", "No summary")
            session_options.append({
                "label": f"{user} - {msg_count} msgs - {summary[:30]}...",
                "value": sess.get("session_id")
            })
        
        if session_options:
            selected_session = st.selectbox(
                "Select a previous session:",
                options=session_options,
                format_func=lambda x: x["label"],
                key="session_selector"
            )
            
            if st.button("📂 Resume Session", use_container_width=True):
                try:
                    response = requests.post(
                        f"{RESUME_SESSION_ENDPOINT}/{selected_session['value']}"
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    st.session_state.session_id = selected_session["value"]
                    st.session_state.conversation_history = []
                    
                    st.success(f"✅ Resumed session")
                    st.info(data.get("message", ""))
                    st.rerun()
                except Exception as e:
                    st.error(f"Error resuming session: {e}")
    
    st.markdown("---")
    
    # Search Sessions
    st.subheader("🔍 Search Sessions")
    search_keyword = st.text_input("Search by keyword:", placeholder="e.g., delhi, refund, booking")
    
    if search_keyword:
        try:
            search_response = requests.get(
                f"{SEARCH_ENDPOINT}?keyword={search_keyword}"
            )
            search_response.raise_for_status()
            search_results = search_response.json().get("sessions", [])
            
            if search_results:
                st.write(f"Found {len(search_results)} session(s):")
                for result in search_results[:5]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"👤 {result.get('user_name', 'Unknown')}")
                        st.caption(result.get('summary', 'No summary'))
                    with col2:
                        if st.button("Load", key=f"load_{result['session_id']}"):
                            try:
                                resume_response = requests.post(
                                    f"{RESUME_SESSION_ENDPOINT}/{result['session_id']}"
                                )
                                resume_response.raise_for_status()
                                st.session_state.session_id = result['session_id']
                                st.session_state.conversation_history = []
                                st.success("✅ Session loaded!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error loading: {e}")
            else:
                st.info("No sessions found with this keyword")
        except Exception as e:
            st.error(f"Search error: {e}")

# Main Chat Area
st.markdown("---")

if not st.session_state.session_id:
    st.info("🚀 Click '➕ New Session' to start a conversation or select a previous session from the sidebar")
else:
    # Conversation History Display
    if st.session_state.conversation_history:
        st.subheader("📝 Conversation History")
        
        for i, message in enumerate(st.session_state.conversation_history):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
    
    # Query Input
    st.subheader("💬 Your Message")
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_query = st.text_input(
            "Ask me anything about flights, policies, or bookings:",
            placeholder="e.g., Show flights from Delhi to Mumbai tomorrow",
            key="query_input"
        )
    
    with col2:
        send_button = st.button("Send ➤", use_container_width=True, key="send_btn")
    
    # Process query
    if send_button and user_query:
        try:
            with st.spinner("🤖 Thinking..."):
                response = requests.post(
                    QUERY_ENDPOINT,
                    json={
                        "query": user_query,
                        "session_id": st.session_state.session_id,
                        "user_name": st.session_state.user_name
                    }
                )
                response.raise_for_status()
                api_response = response.json()
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "role": "user",
                    "content": user_query
                })
                
                assistant_message = api_response.get("message", api_response.get("response", "No response"))
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                # Update session ID if new
                if api_response.get("is_new_session"):
                    st.session_state.session_id = api_response.get("session_id")
                    st.success("✅ New session created!")
                
                st.rerun()
                
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to API at {API_BASE_URL}")
            st.info("Make sure FastAPI is running: `uvicorn api/main:app --host 0.0.0.0 --port 8000`")
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ API Error: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    elif send_button:
        st.warning("⚠️ Please enter a message")

st.markdown("---")
st.markdown("Made with ❤️ | Powered by AI")