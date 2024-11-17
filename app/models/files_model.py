from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from app.shared.config.db import Base
import enum

class Files(Base):
    __tablename__ = "post_files"
    id_file = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id_post", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    url = Column(String(255), nullable=False)
    
    # Relación con ForumPosts
    post = relationship("ForumPosts", back_populates="files")
    
    