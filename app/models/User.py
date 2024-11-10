from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum, Text, LargeBinary
from app.shared.config.db import Base
from app.models.interfaces import EducationLevel, State


class User(Base):
    __tablename__ = "user"
    id_user = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), nullable=False)
    background_image_url = Column(String(255), nullable=True)
    profile_image_url = Column(String(255), nullable=True)
    lastname = Column(String(255), nullable=False)
    mail = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    user_type = Column(String(255), nullable=False)
    education_level = Column(Enum(EducationLevel), nullable=False)
    creation_date = Column(DateTime, nullable=False)
    state = Column(Enum(State), nullable=True, default=State.Activo)
    
    deleted = Column(Boolean, nullable=True, default=False)