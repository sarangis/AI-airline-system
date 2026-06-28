"""
Conversational message handler for the airline support system.
Manages conversation history, context, and generates friendly responses.
"""

from typing import List, Dict, Optional
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import os


class ConversationHistory:
    """Manages conversation history and context."""
    
    def __init__(self, max_history: int = 100, session_id: Optional[str] = None):
        """
        Initialize conversation history manager.
        
        Args:
            max_history: Maximum number of messages to keep in memory
            session_id: Optional session ID (for persistence)
        """
        self.messages: List[Dict] = []
        self.max_history = max_history
        self.session_start = datetime.now()
        self.user_name: Optional[str] = None
        self.booking_ref: Optional[str] = None
        self.session_id: str = session_id or self._generate_session_id()
    
    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID."""
        import uuid
        return str(uuid.uuid4())
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Add a message to conversation history.
        
        Args:
            role: "user" or "assistant"
            content: Message content
            metadata: Additional metadata (query_type, corrections, etc.)
        """
        message = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.messages.append(message)
        
        # Keep only recent messages in memory (older ones in db)
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_conversation_context(self, include_all: bool = True, max_messages: int = None) -> str:
        """
        Get formatted conversation context for LLM.
        
        Args:
            include_all: Include all messages or just recent ones
            max_messages: Maximum messages to include (None = all or recent)
            
        Returns:
            Formatted conversation context
        """
        if not self.messages:
            return ""
        
        # Determine which messages to include
        if include_all:
            messages_to_use = self.messages
        else:
            messages_to_use = self.messages[-(max_messages or 5):]
        
        context = "Conversation History:\n"
        for msg in messages_to_use:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        return context
    
    def get_summary(self) -> str:
        """Get a brief summary of the conversation topics."""
        if not self.messages:
            return "No conversation yet"
        
        user_messages = [m['content'] for m in self.messages if m['role'] == 'user']
        topics = []
        
        # Extract key topics from user messages
        keywords = ['flight', 'booking', 'cancel', 'refund', 'delay', 'change', 'baggage']
        for msg in user_messages:
            for keyword in keywords:
                if keyword.lower() in msg.lower():
                    topics.append(keyword)
        
        return f"Topics discussed: {', '.join(set(topics))}" if topics else "General inquiry"
    
    def get_last_user_query(self) -> Optional[str]:
        """Get the last user query."""
        for msg in reversed(self.messages):
            if msg["role"] == "user":
                return msg["content"]
        return None
    
    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []
        self.session_start = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert conversation to dictionary."""
        return {
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "user_name": self.user_name,
            "booking_ref": self.booking_ref,
            "message_count": len(self.messages),
            "messages": self.messages,
            "summary": self.get_summary()
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load conversation from dictionary."""
        self.session_id = data.get("session_id", self.session_id)
        self.user_name = data.get("user_name")
        self.booking_ref = data.get("booking_ref")
        self.messages = data.get("messages", [])
        if data.get("session_start"):
            self.session_start = datetime.fromisoformat(data["session_start"])


def create_conversational_response_formatter(llm):
    """
    Creates a formatter that makes responses more conversational and friendly.
    
    Args:
        llm: The language model instance
        
    Returns:
        A function that formats responses conversationally
    """
    
    formatter_prompt = ChatPromptTemplate.from_template(
        """You are a friendly and professional airline customer support assistant.
Your job is to take technical responses and make them conversational and easy to understand.

ORIGINAL RESPONSE: {response}

CONVERSATION HISTORY:
{conversation_context}

USER'S LAST QUERY: {user_query}

FORMATTING GUIDELINES:
1. Be warm and professional
2. Start with a greeting or acknowledgment (only if starting new conversation)
3. Break down complex information into easy-to-understand parts
4. Use emojis sparingly (only if appropriate)
5. End with a helpful follow-up question or offer
6. If the response is technical (like SQL results), translate it to plain English
7. Maintain the user's tone (formal/casual based on their query)
8. Keep responses concise but complete

Transform the technical response into a natural, conversational message:"""
    )
    
    formatter_chain = formatter_prompt | llm | StrOutputParser()
    
    def format_response(
        response: str,
        conversation_history: ConversationHistory,
        user_query: str
    ) -> str:
        """
        Format response to be more conversational.
        
        Args:
            response: Technical response from the system
            conversation_history: Conversation history for context
            user_query: The user's original query
            
        Returns:
            Conversational, formatted response
        """
        try:
            formatted = formatter_chain.invoke({
                "response": response,
                "conversation_context": conversation_history.get_conversation_context(),
                "user_query": user_query
            })
            return formatted
        except Exception as e:
            print(f"Error formatting response: {e}")
            return response
    
    return format_response


def create_context_aware_responder(llm):
    """
    Creates a responder that uses conversation history for context.
    
    Args:
        llm: The language model instance
        
    Returns:
        A function that generates context-aware responses
    """
    
    responder_prompt = ChatPromptTemplate.from_template(
        """You are a helpful airline customer support assistant.

CONVERSATION HISTORY:
{conversation_context}

USER'S NEW MESSAGE: {user_query}

Based on the conversation history and the new user message, provide a contextual response.
Consider:
1. Previous queries and their context
2. Any mentioned booking references or preferences
3. Repeated issues or concerns
4. Continuity with the conversation

Generate a natural, helpful response:"""
    )
    
    responder_chain = responder_prompt | llm | StrOutputParser()
    
    def respond(
        user_query: str,
        conversation_history: ConversationHistory
    ) -> str:
        """
        Generate context-aware response.
        
        Args:
            user_query: The user's query
            conversation_history: Conversation history for context
            
        Returns:
            Context-aware response
        """
        try:
            response = responder_chain.invoke({
                "conversation_context": conversation_history.get_conversation_context(),
                "user_query": user_query
            })
            return response
        except Exception as e:
            print(f"Error generating context-aware response: {e}")
            return user_query
    
    return respond


def create_greeting_generator(llm):
    """
    Creates a generator for initial greetings based on conversation start.
    
    Args:
        llm: The language model instance
        
    Returns:
        A function that generates personalized greetings
    """
    
    greeting_prompt = ChatPromptTemplate.from_template(
        """You are a friendly airline customer support assistant starting a new conversation.
        
Generate a warm, welcoming greeting that:
1. Introduces yourself as an airline support assistant
2. Is brief (1-2 sentences max)
3. Invites the user to ask questions or get help
4. Is professional yet friendly

Current time: {current_time}
Generate the greeting:"""
    )
    
    greeting_chain = greeting_prompt | llm | StrOutputParser()
    
    def generate_greeting() -> str:
        """Generate initial greeting."""
        try:
            greeting = greeting_chain.invoke({
                "current_time": datetime.now().strftime("%H:%M")
            })
            return greeting
        except Exception as e:
            print(f"Error generating greeting: {e}")
            return "Hello! I'm your airline support assistant. How can I help you today?"
    
    return generate_greeting


def create_clarification_asker(llm):
    """
    Creates a function that asks clarifying questions when needed.
    
    Args:
        llm: The language model instance
        
    Returns:
        A function that generates clarifying questions
    """
    
    clarification_prompt = ChatPromptTemplate.from_template(
        """You are a helpful airline customer support assistant.
The user's query is somewhat ambiguous or incomplete. Generate 2-3 clarifying questions
to better understand their needs.

USER'S QUERY: {user_query}

Format the clarifying questions naturally, as a conversational follow-up.
Keep it brief and helpful."""
    )
    
    clarification_chain = clarification_prompt | llm | StrOutputParser()
    
    def ask_clarifications(user_query: str) -> str:
        """
        Ask clarifying questions about ambiguous queries.
        
        Args:
            user_query: The user's query
            
        Returns:
            Clarifying questions
        """
        try:
            clarifications = clarification_chain.invoke({"user_query": user_query})
            return clarifications
        except Exception as e:
            print(f"Error generating clarifications: {e}")
            return ""
    
    return ask_clarifications


def build_conversational_response(
    technical_response: str,
    user_query: str,
    conversation_history: ConversationHistory,
    response_formatter: callable,
    query_metadata: Optional[Dict] = None
) -> Dict:
    """
    Build a complete conversational response with formatting.
    
    Args:
        technical_response: The technical response from the system
        user_query: The user's original query
        conversation_history: Conversation history
        response_formatter: Function to format responses
        query_metadata: Additional metadata about the query
        
    Returns:
        Dictionary with formatted response and metadata
    """
    
    # Format the response conversationally
    conversational_response = response_formatter(
        technical_response,
        conversation_history,
        user_query
    )
    
    # Build response object
    response_object = {
        "message": conversational_response,
        "original_response": technical_response,
        "query_metadata": query_metadata or {},
        "timestamp": datetime.now().isoformat(),
        "follow_up_suggestion": None
    }
    
    # Add follow-up suggestions if available
    if query_metadata and query_metadata.get("query_type") == "flight_search":
        response_object["follow_up_suggestion"] = "Would you like to book one of these flights or need more information?"
    elif query_metadata and query_metadata.get("query_type") == "booking":
        response_object["follow_up_suggestion"] = "Is there anything else you'd like to know about your booking?"
    
    return response_object


def create_session_summarizer(llm):
    """
    Creates a function that summarizes a conversation session.
    
    Args:
        llm: The language model instance
        
    Returns:
        A function that generates session summaries
    """
    
    summary_prompt = ChatPromptTemplate.from_template(
        """Summarize the following conversation between a user and airline support assistant.
Focus on:
1. Main issues raised
2. Resolutions provided
3. Action items (if any)
4. User satisfaction indicators

CONVERSATION:
{conversation_text}

Provide a concise summary (3-5 sentences):"""
    )
    
    summary_chain = summary_prompt | llm | StrOutputParser()
    
    def summarize(conversation_history: ConversationHistory) -> str:
        """
        Summarize a conversation.
        
        Args:
            conversation_history: The conversation history
            
        Returns:
            Summary of the conversation
        """
        if not conversation_history.messages:
            return "No conversation to summarize."
        
        # Format conversation for summary
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history.messages
        ])
        
        try:
            summary = summary_chain.invoke({"conversation_text": conversation_text})
            return summary
        except Exception as e:
            print(f"Error summarizing conversation: {e}")
            return "Unable to generate summary."
    
    return summarize
