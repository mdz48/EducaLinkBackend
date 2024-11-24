from sqlalchemy import Column, ForeignKey, Integer
from app.shared.config.db import Base


class SaleChat(Base):
    __tablename__ = "sale_chat" 
    id_sale_chat = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
