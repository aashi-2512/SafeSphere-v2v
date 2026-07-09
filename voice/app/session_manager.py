from datetime import datetime
from uuid import uuid4


class SessionManager:
    def __init__(self):
        # Stores all active sessions
        self.sessions = {}

    def create_session(self):
        """
        Create a new emergency session.
        """
        session_id = str(uuid4())

        self.sessions[session_id] = {
            "created_at": datetime.utcnow(),
            "broadcaster": None,
            "listeners": set()
        }

        return session_id

    def get_session(self, session_id):
        """
        Return session details if it exists.
        """
        return self.sessions.get(session_id)

    def delete_session(self, session_id):
        """
        Remove a session completely.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]

    def session_exists(self, session_id):
        return session_id in self.sessions


# Singleton instance used throughout the app
session_manager = SessionManager()