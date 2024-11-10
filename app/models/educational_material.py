from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from app.shared.config.db import Base
from app.models.interfaces import FileType, EducationLevel


class EducationalMaterial(Base):
    __tablename__ = "educational_material"
    id_material = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    publication_date = Column(DateTime, nullable=False)
    file_url = Column(String(255), nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id_category", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    education_level = Column(Enum(EducationLevel), nullable=False)