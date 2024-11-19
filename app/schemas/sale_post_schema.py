from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.user_schema import UserResponse

class SalePostBase(BaseModel):
    title: str
    description: str
    price: float
    image_url: str
    model_config = ConfigDict(from_attributes=True)
    sale_type: str | None = "Material_didactico"

class SalePostCreate(SalePostBase):
    pass

class SalePostResponse(SalePostBase):
    id_sale_post: int
    publication_date: datetime
    status: str
    seller: UserResponse
