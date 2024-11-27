from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer
from app.models.interfaces import EducationLevel
from app.schemas.company_schema import CompanyResponse
from app.schemas.forum_schema import ForumResponse
from app.schemas.user_schema import UserResponse
from app.shared.utils.date_reformater import format_date
from typing import List

class AdsBase(BaseModel):
    title: str
    description: str
    image_url: str
    link: str
    
    model_config = ConfigDict(from_attributes=True)
    

class AdsResponse(AdsBase):
    id_ad: int
    created_at: datetime

