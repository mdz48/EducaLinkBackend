from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer

from app.schemas.user_schema import UserResponse
from app.shared.utils.date_reformater import format_date

class ForumBase(BaseModel):
    name: str
    description: str
    background_image_url: str | None = "https://educalinkbucket.s3.us-east-1.amazonaws.com/default_portrait_white.png"
    image_url: str | None = "https://educalinkbucket.s3.us-east-1.amazonaws.com/default_group.png"
    education_level: str | None = 'Primaria'
    grade: int | None = 1
    privacy: str | None = 'Publico'

    model_config = ConfigDict(from_attributes=True)
    
class ForumCreate(ForumBase):
    password: str | None = '' 

class ForumResponse(ForumBase):
    id_forum: int
    creation_date: datetime
    user_name: str
    id_user: int
    users_count: int | None = 1
    
class ForumResponseWithCreator(ForumResponse):
    creator: UserResponse

    # @field_serializer('creation_date')
    # def serialize_datetime(self, creation_date: datetime):
    #     return format_date(creation_date)
