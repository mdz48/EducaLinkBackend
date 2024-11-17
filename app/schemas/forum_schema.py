from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer

from app.shared.utils.date_reformater import format_date

class ForumBase(BaseModel):
    name: str
    description: str
    # state: str
    background_image_url: str | None = "https://drive.google.com/file/d/1CWU_gcEd4bxP4wgsggAioAqH_eSaroeu/view?usp=drive_link"
    image_url: str | None = "https://drive.google.com/file/d/1GXGIlNMVwBZ7q2DwgYZawmGlof1y7Zde/view?usp=drive_link"
    education_level: str | None = 'Primaria'
    privacy: str | None = 'Publico'
    password: str | None = None 

    model_config = ConfigDict(from_attributes=True)
    
class ForumCreate(ForumBase):
    pass

class ForumResponse(ForumBase):
    id_forum: int
    creation_date: datetime
    user_name: str
    id_user: int
    users_count: int | None = 1
    
    
    # @field_serializer('creation_date')
    # def serialize_datetime(self, creation_date: datetime):
    #     return format_date(creation_date)
