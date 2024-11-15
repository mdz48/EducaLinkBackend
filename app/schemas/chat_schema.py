from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ChatBase(BaseModel):
    # sender_id: int
    receiver_id: int

    model_config = ConfigDict(from_attributes=True)
    
class ChatCreate(ChatBase):
    pass

class ChatResponse(ChatBase):
    id_chat: int
    sender_id: int
    receiver_id: int

