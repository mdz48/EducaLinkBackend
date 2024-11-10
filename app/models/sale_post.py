from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum, Text, Numeric
from app.shared.config.db import Base
from app.models.interfaces import PostStatus


class SalePost(Base):
    __tablename__ = "sale_posts"
    id_sale_post = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    url = Column(String(255), nullable=False)
    publication_date = Column(DateTime, nullable=False)
    status = Column(Enum(PostStatus), nullable=False)
    seller_id = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

