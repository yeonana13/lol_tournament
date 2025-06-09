"""세션 관리 유틸리티"""
import uuid
import asyncio
from typing import Dict, List, Optional

class GameSession:
    def __init__(self, session_id: str, host_id: int, title: str, participants: List[int]):
        self.session_id = session_id
        self.host_id = host_id
        self.title = title
        self.participants = participants
        self.created_at = asyncio.get_event_loop().time()
        self.status = 'waiting'
        
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'host_id': self.host_id,
            'title': self.title,
            'participants': self.participants,
            'status': self.status,
            'created_at': self.created_at
        }

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
    
    def create_session(self, host_id: int, title: str, participants: List[int]) -> str:
        session_id = str(uuid.uuid4())
        session = GameSession(session_id, host_id, title, participants)
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[GameSession]:
        return self.sessions.get(session_id)
    
    def update_session_status(self, session_id: str, status: str) -> bool:
        if session_id in self.sessions:
            self.sessions[session_id].status = status
            return True
        return False
    
    def remove_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

session_manager = SessionManager()
