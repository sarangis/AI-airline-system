# api/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

# Ensure your PYTHONPATH is set correctly in Codespaces for this import to work.
# Often, adding 'export PYTHONPATH=$PYTHONPATH:.' to your .bashrc or .zshrc in Codespaces helps.
from src.core_logic import process_user_query_with_guardrails
from src.conversation_manager import (
    ConversationHistory, 
    create_conversational_response_formatter,
    create_greeting_generator,
    create_clarification_asker,
    build_conversational_response
)
from src.conversation_store import ConversationStore
from langchain_openai import ChatOpenAI

load_dotenv() # <-- Load environment variables from .env

# Initialize LLM for conversational features
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    temperature=0.5,  # Slightly higher for conversational variety
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Initialize conversation tools
response_formatter = create_conversational_response_formatter(llm)
greeting_generator = create_greeting_generator(llm)
clarification_asker = create_clarification_asker(llm)

# Initialize conversation storage
store = ConversationStore("data/conversations")

# Global conversation histories (in memory for current sessions)
conversations: Dict[str, ConversationHistory] = {}

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_name: Optional[str] = None
    booking_ref: Optional[str] = None

class ConversationResponse(BaseModel):
    message: str
    original_response: str
    session_id: str
    timestamp: str
    follow_up_suggestion: Optional[str] = None
    is_new_session: bool = False

class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    user_name: Optional[str]
    booking_ref: Optional[str]
    session_start: str
    summary: Optional[str] = None

class NewSessionResponse(BaseModel):
    session_id: str
    message: str
    status: str = "new_session_started"

class SessionListResponse(BaseModel):
    sessions: List[Dict]
    total_count: int

app = FastAPI()

def get_or_create_session(session_id: Optional[str], user_name: Optional[str] = None) -> tuple[str, ConversationHistory]:
    """
    Get existing or create new conversation session.
    Loads from storage if not in memory.
    """
    if session_id and session_id in conversations:
        return session_id, conversations[session_id]
    
    # Try to load from storage if session_id provided
    if session_id:
        stored_data = store.load_conversation(session_id)
        if stored_data:
            conv = ConversationHistory(session_id=session_id)
            conv.from_dict(stored_data)
            conversations[session_id] = conv
            return session_id, conv
    
    # Create new session
    import uuid
    new_session_id = session_id or str(uuid.uuid4())
    conv = ConversationHistory(session_id=new_session_id)
    if user_name:
        conv.user_name = user_name
    conversations[new_session_id] = conv
    return new_session_id, conv

@app.post("/new-session")
async def new_session(user_name: Optional[str] = None) -> NewSessionResponse:
    """
    Start a completely new session, discarding any previous context.
    """
    import uuid
    session_id = str(uuid.uuid4())
    conv = ConversationHistory(session_id=session_id)
    if user_name:
        conv.user_name = user_name
    
    conversations[session_id] = conv
    greeting = greeting_generator()
    
    return NewSessionResponse(
        session_id=session_id,
        message=greeting,
        status="new_session_started"
    )

@app.post("/query")
async def process_query(request: QueryRequest) -> ConversationResponse:
    """
    Process a user query with conversational messaging.
    """
    try:
        # Get or create conversation session
        is_new = request.session_id is None
        session_id, conversation = get_or_create_session(request.session_id, request.user_name)
        
        # Update session info if provided
        if request.user_name:
            conversation.user_name = request.user_name
        if request.booking_ref:
            conversation.booking_ref = request.booking_ref
        
        # Add user query to history
        conversation.add_message("user", request.query)
        
        # Process the query through core logic
        technical_response = process_user_query_with_guardrails(request.query)
        
        # Extract metadata if available (in future, enhance this)
        query_metadata = {
            "query_type": "general",
            "processed_at": None
        }
        
        # Format response conversationally using FULL context
        conversational_response = response_formatter(
            technical_response,
            conversation,
            request.query
        )
        
        # Add assistant response to history
        conversation.add_message("assistant", conversational_response)
        
        # Save conversation to storage
        store.save_conversation(session_id, conversation.to_dict())
        
        # Build response object
        from datetime import datetime
        response = ConversationResponse(
            message=conversational_response,
            original_response=technical_response,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            follow_up_suggestion=query_metadata.get("follow_up_suggestion"),
            is_new_session=is_new
        )
        
        return response
        
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: QueryRequest) -> ConversationResponse:
    """
    Chat endpoint - alias for /query with same functionality.
    """
    return await process_query(request)

@app.get("/session/{session_id}")
async def get_session_info(session_id: str) -> SessionInfo:
    """
    Get conversation session information.
    """
    if session_id not in conversations:
        # Try loading from storage
        stored_data = store.load_conversation(session_id)
        if not stored_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        conv = ConversationHistory(session_id=session_id)
        conv.from_dict(stored_data)
    else:
        conv = conversations[session_id]
    
    return SessionInfo(
        session_id=session_id,
        message_count=len(conv.messages),
        user_name=conv.user_name,
        booking_ref=conv.booking_ref,
        session_start=conv.session_start.isoformat(),
        summary=conv.get_summary()
    )

@app.get("/sessions")
async def list_sessions(
    user_name: Optional[str] = None,
    limit: int = 20
) -> SessionListResponse:
    """
    List all previous sessions or filter by user.
    """
    sessions = store.list_sessions(user_name=user_name, limit=limit)
    
    return SessionListResponse(
        sessions=sessions,
        total_count=len(sessions)
    )

@app.post("/resume-session/{session_id}")
async def resume_session(session_id: str, user_name: Optional[str] = None) -> Dict:
    """
    Resume a previous conversation session.
    Loads the session and generates a welcome back message.
    """
    stored_data = store.load_conversation(session_id)
    if not stored_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Load session into memory
    conv = ConversationHistory(session_id=session_id)
    conv.from_dict(stored_data)
    conversations[session_id] = conv
    
    # Generate welcome back message
    summary = conv.get_summary()
    message = f"Welcome back, {conv.user_name or 'there'}! I see we last talked about {summary}. How can I help you today?"
    
    return {
        "session_id": session_id,
        "message": message,
        "status": "session_resumed",
        "previous_message_count": len(conv.messages),
        "summary": summary
    }

@app.get("/search-sessions")
async def search_sessions(keyword: str) -> SessionListResponse:
    """
    Search previous conversations by keyword.
    Searches in user name, booking reference, and conversation summary.
    """
    sessions = store.search_conversations(keyword)
    
    return SessionListResponse(
        sessions=sessions,
        total_count=len(sessions)
    )

@app.get("/sessions/stats")
async def get_sessions_stats() -> Dict:
    """
    Get statistics about stored conversations.
    """
    return store.get_session_stats()

@app.get("/greeting")
async def get_greeting() -> Dict[str, str]:
    """
    Get an initial greeting message.
    """
    greeting = greeting_generator()
    return {"greeting": greeting, "session_hint": "Use the /query endpoint with your first query"}

@app.post("/clarify")
async def clarify_query(request: QueryRequest) -> Dict[str, str]:
    """
    Get clarifying questions for an ambiguous query.
    """
    clarifications = clarification_asker(request.query)
    return {"clarifications": clarifications, "original_query": request.query}

@app.delete("/session/{session_id}")
async def clear_session(session_id: str) -> Dict[str, str]:
    """
    Clear/delete a conversation session from memory and storage.
    """
    deleted = False
    
    if session_id in conversations:
        del conversations[session_id]
        deleted = True
    
    if store.delete_conversation(session_id):
        deleted = True
    
    if deleted:
        return {"status": "success", "message": "Session cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/")
async def read_root():
    return {
        "message": "Airline Customer Support API with Persistent Conversations",
        "endpoints": {
            "conversation": {
                "new_session": "POST /new-session - Start a completely new session",
                "query": "POST /query - Process a query (creates session if needed)",
                "chat": "POST /chat - Chat endpoint (same as /query)",
                "greeting": "GET /greeting - Get initial greeting",
                "clarify": "POST /clarify - Get clarifying questions"
            },
            "sessions": {
                "list": "GET /sessions - List all previous sessions",
                "list_by_user": "GET /sessions?user_name=John - List sessions for a user",
                "search": "GET /search-sessions?keyword=delhi - Search sessions",
                "stats": "GET /sessions/stats - Get session statistics",
                "info": "GET /session/{session_id} - Get session details",
                "resume": "POST /resume-session/{session_id} - Resume a previous session",
                "delete": "DELETE /session/{session_id} - Delete a session"
            },
            "health": "GET /health - Check API health"
        },
        "features": [
            "Multi-turn conversations",
            "Full conversation history persistence",
            "Start new sessions anytime",
            "Resume previous conversations",
            "Search past conversations",
            "Spell correction & LLM enhancement",
            "Conversational responses",
            "Session statistics"
        ],
        "example_flow": {
            "1_start_new": "POST /new-session {user_name: 'John'}",
            "2_send_query": "POST /query {query: 'flights to goa', session_id: 'abc-123'}",
            "3_continue": "POST /query {query: 'book the cheapest', session_id: 'abc-123'}",
            "4_list_old": "GET /sessions",
            "5_resume_old": "POST /resume-session/old-session-id"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_sessions": len(conversations),
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }