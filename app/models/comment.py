from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from app.shared.config.db import Base
import enum



class Comment(Base):
    __tablename__ = "comment"
    id_comment = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    comment_text = Column(Text, nullable=False)
    comment_date = Column(DateTime, nullable=False)
    post_id = Column(Integer, ForeignKey("forum_posts.id_post", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    post = relationship("ForumPosts", back_populates="comments")