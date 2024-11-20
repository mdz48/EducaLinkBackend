from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum, Text
from app.shared.config.db import Base
from sqlalchemy.orm import relationship
from app.models.interfaces import GroupType, EducationLevel


class Forum(Base):
    __tablename__ = "forum"
    id_forum = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), nullable=False)
    background_image_url = Column(String(255), nullable=True, default=None)
    image_url = Column(String(255), nullable=True, default=None)
    description = Column(Text, nullable=False)
    creation_date = Column(DateTime, nullable=False)
    education_level = Column(Enum(EducationLevel), nullable=False)
    grade = Column(Integer, nullable=False)
    privacy = Column(Enum(GroupType), nullable=False)
    user_name = Column(String(100), nullable=False)
    id_user = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    password = Column(String(255), nullable=True, default=None)
    
