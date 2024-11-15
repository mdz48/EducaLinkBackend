from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer
from app.models.interfaces import EducationLevel
from app.schemas.user_schema import UserResponse
from app.shared.utils.date_reformater import format_date

class PostBase(BaseModel):
    content: str
    title: str
    forum_id: int

    model_config = ConfigDict(from_attributes=True)
    
class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id_post: int
    publication_date: datetime
    user: UserResponse
    comment_count: int | None = 0

    model_config = ConfigDict(from_attributes=True)

    # @field_serializer('publication_date')
    # def serialize_datetime(self, publication_date: datetime):
    #     return format_date(publication_date)

