from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.user_schema import UserResponse

class CommentBase(BaseModel):
    comment_text: str
    post_id: int

    model_config = ConfigDict(from_attributes=True)
    
class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id_comment: int
    comment_date: datetime
    user_id: int
    
class CommentResponseWithUser(CommentResponse):
    user: UserResponse
    comment_date: datetime