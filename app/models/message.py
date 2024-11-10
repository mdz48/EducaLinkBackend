from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime
from app.shared.config.db import Base

class Message(Base):
    __tablename__ = "messages"
    id_message = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chat.id_chat", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    date_message = Column(DateTime, nullable=False)