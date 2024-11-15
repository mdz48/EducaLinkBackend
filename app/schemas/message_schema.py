from datetime import datetime
from pydantic import BaseModel, ConfigDict

class MessageBase(BaseModel):
    message: str
    chat_id: int
    date_message: datetime

    model_config = ConfigDict(from_attributes=True)

class MessageCreate(MessageBase):
    date_message: datetime | None = None

class MessageResponse(MessageBase):
    id_message: int
    sender_id : int
