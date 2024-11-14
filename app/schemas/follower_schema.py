from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class FollowerResponse(BaseModel):
    id_follower: int
    id_user: int
    follower_id: int
    

    model_config = ConfigDict(from_attributes=True)
    

