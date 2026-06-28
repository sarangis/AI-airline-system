"""
Conversation storage and persistence layer.
Saves and loads conversation history from storage.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class ConversationStore:
    """Handles persistence of conversations."""
    
    def __init__(self, storage_dir: str = "data/conversations"):
        """
        Initialize conversation store.
        
        Args:
            storage_dir: Directory to store conversation files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._load_index()
    
    def _load_index(self) -> None:
        """Load or create the conversation index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}
            self._save_index()
    
    def _save_index(self) -> None:
        """Save the conversation index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def save_conversation(self, session_id: str, conversation_data: Dict) -> bool:
        """
        Save a conversation to storage.
        
        Args:
            session_id: Unique session identifier
            conversation_data: Conversation data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Save conversation file
            file_path = self.storage_dir / f"{session_id}.json"
            with open(file_path, 'w') as f:
                json.dump(conversation_data, f, indent=2)
            
            # Update index
            self.index[session_id] = {
                "user_name": conversation_data.get("user_name"),
                "booking_ref": conversation_data.get("booking_ref"),
                "message_count": conversation_data.get("message_count", 0),
                "session_start": conversation_data.get("session_start"),
                "summary": conversation_data.get("summary", ""),
                "last_updated": datetime.now().isoformat()
            }
            self._save_index()
            
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def load_conversation(self, session_id: str) -> Optional[Dict]:
        """
        Load a conversation from storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Conversation data or None if not found
        """
        try:
            file_path = self.storage_dir / f"{session_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return None
    
    def list_sessions(self, user_name: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        List all sessions or sessions for a specific user.
        
        Args:
            user_name: Filter by user name (optional)
            limit: Maximum number of sessions to return
            
        Returns:
            List of session info
        """
        sessions = []
        
        # Sort by last_updated, most recent first
        sorted_sessions = sorted(
            self.index.items(),
            key=lambda x: x[1].get("last_updated", ""),
            reverse=True
        )
        
        for session_id, session_info in sorted_sessions[:limit]:
            if user_name and session_info.get("user_name") != user_name:
                continue
            
            sessions.append({
                "session_id": session_id,
                **session_info
            })
        
        return sessions
    
    def delete_conversation(self, session_id: str) -> bool:
        """
        Delete a conversation from storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.storage_dir / f"{session_id}.json"
            if file_path.exists():
                file_path.unlink()
            
            if session_id in self.index:
                del self.index[session_id]
                self._save_index()
            
            return True
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def search_conversations(self, keyword: str) -> List[Dict]:
        """
        Search conversations by keyword.
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching sessions
        """
        matching_sessions = []
        keyword_lower = keyword.lower()
        
        for session_id, session_info in self.index.items():
            # Search in user name, booking ref, and summary
            user_name = session_info.get("user_name") or ""
            booking_ref = session_info.get("booking_ref") or ""
            summary = session_info.get("summary") or ""
            
            if (keyword_lower in str(user_name).lower() or
                keyword_lower in str(booking_ref).lower() or
                keyword_lower in str(summary).lower()):
                
                matching_sessions.append({
                    "session_id": session_id,
                    **session_info
                })
        
        return matching_sessions
    
    def get_session_stats(self) -> Dict:
        """Get statistics about stored conversations."""
        total_sessions = len(self.index)
        total_messages = sum(s.get("message_count", 0) for s in self.index.values())
        
        # Get unique users
        unique_users = set()
        for session in self.index.values():
            if session.get("user_name"):
                unique_users.add(session["user_name"])
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "unique_users": len(unique_users),
            "storage_path": str(self.storage_dir)
        }
