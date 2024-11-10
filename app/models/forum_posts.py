from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from app.shared.config.db import Base
import enum
from app.models.interfaces import EducationLevel

class ForumPosts(Base):
    __tablename__ = "forum_posts"
    id_post = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(100), nullable=False)
    user_education_level = Column(Enum(EducationLevel), nullable=False)
    user_profile_image_url = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    publication_date = Column(DateTime, nullable=False)
    forum_id = Column(Integer, ForeignKey("forum.id_forum", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
