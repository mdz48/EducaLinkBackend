from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.user_schema import UserResponse

class MessageBase(BaseModel):
    message: str
    chat_id: int

    model_config = ConfigDict(from_attributes=True)

class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id_message: int
    sender: UserResponse
    date_message: datetime
