from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SalePostBase(BaseModel):
    title: str
    description: str
    price: float
    url: str
    # publication_date: datetime
    status: str
    # seller_id: int
    model_config = ConfigDict(from_attributes=True)

class SalePostCreate(SalePostBase):
    # publication_date: datetime | None = None
    pass

class SalePostResponse(SalePostBase):
    id_sale_post: int
    publication_date: datetime
    status: str
    seller_id: int
