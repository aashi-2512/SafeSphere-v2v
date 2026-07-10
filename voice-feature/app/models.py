from pydantic import BaseModel


class SessionResponse(BaseModel):
    session_id: str
    broadcaster_token: str
    listener_token: str