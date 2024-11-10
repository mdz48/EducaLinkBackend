from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserForumBase(BaseModel):
    id_user: int
    id_forum: int
    join_date: datetime
    background_image_url: str | None = "https://drive.google.com/file/d/1CWU_gcEd4bxP4wgsggAioAqH_eSaroeu/view?usp=drive_link"
    image_url: str | None = "https://drive.google.com/file/d/1GXGIlNMVwBZ7q2DwgYZawmGlof1y7Zde/view?usp=drive_link"
    model_config = ConfigDict(from_attributes=True)
    
class UserForumCreate(UserForumBase):
    join_date: datetime | None = None

class UserForumResponse(UserForumBase):
    id_member: int
    id_user: int
    id_forum: int

