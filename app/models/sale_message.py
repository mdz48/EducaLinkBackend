from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime
from app.shared.config.db import Base

class SaleMessage(Base):
    __tablename__ = "sale_message"
    id_sale_message = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    sale_chat_id = Column(Integer, ForeignKey("sale_chat.id_sale_chat", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    date_message = Column(DateTime, nullable=False)