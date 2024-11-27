from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from app.shared.config.db import Base


class Ads(Base):
    __tablename__ = "ads"
    id_ad = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=False)
    link = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True)
