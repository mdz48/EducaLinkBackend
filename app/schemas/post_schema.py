from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer
from app.models.interfaces import EducationLevel
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
    user_name: str
    user_education_level: EducationLevel
    user_profile_image_url: str | None = "URL_DEFAULT"
    publication_date: datetime
    user_id: int
    comment_count: int | None = 0

    @field_serializer('publication_date')
    def serialize_datetime(self, publication_date: datetime):
        return format_date(publication_date)

