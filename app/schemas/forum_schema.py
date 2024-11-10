from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ForumBase(BaseModel):
    name: str
    description: str
    # state: str
    background_image_url: str | None = "https://drive.google.com/file/d/1CWU_gcEd4bxP4wgsggAioAqH_eSaroeu/view?usp=drive_link"
    image_url: str | None = "https://drive.google.com/file/d/1GXGIlNMVwBZ7q2DwgYZawmGlof1y7Zde/view?usp=drive_link"
    education_level: str
    privacy: str
    password: str | None = None 

    model_config = ConfigDict(from_attributes=True)
    
class ForumCreate(ForumBase):
    creation_date: datetime | None = None

class ForumResponse(ForumBase):
    id_forum: int
    creation_date: datetime
    id_user: int
    education_level: str
