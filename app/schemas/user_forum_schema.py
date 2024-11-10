from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserForumBase(BaseModel):
    id_user: int
    id_forum: int
    join_date: datetime
    model_config = ConfigDict(from_attributes=True)
    
class UserForumCreate(UserForumBase):
    pass

class UserForumResponse(UserForumBase):
    id_member: int
    id_user: int
    id_forum: int

