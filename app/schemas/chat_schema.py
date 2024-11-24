from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user_schema import UserResponse
class ChatBase(BaseModel):
    # sender_id: int
    receiver_id: int

    model_config = ConfigDict(from_attributes=True)
    
class ChatCreate(ChatBase):
    pass

class ChatResponse(BaseModel):
    sender: UserResponse
    receiver: UserResponse
    id_chat: int
    
    model_config = ConfigDict(from_attributes=True)

