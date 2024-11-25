from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer
from app.models.interfaces import EducationLevel
from app.schemas.forum_schema import ForumResponse
from app.schemas.user_schema import UserResponse
from app.shared.utils.date_reformater import format_date
from typing import List

class CompanyBase(BaseModel):
    name: str
    image_url: str
    link: str
    
    model_config = ConfigDict(from_attributes=True)
    

class CompanyResponse(CompanyBase):
    id_company: int
