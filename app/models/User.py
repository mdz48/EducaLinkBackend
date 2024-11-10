from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum, Text
from app.shared.config.db import Base
import enum

class EducationLevel(enum.Enum):
    Primaria = "Primaria"
    Preescolar = "Preescolar"
    
class State(enum.Enum):
    Activo = "Activo"
    Bloqueado = "Bloqueado" 

class User(Base):
    __tablename__ = "user"
    id_user = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=False)
    mail = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    user_type = Column(String(255), nullable=False)
    education_level = Column(Enum(EducationLevel), nullable=False)
    creation_date = Column(DateTime, nullable=False)
    state = Column(Enum(State), nullable=False)
    deleted = Column(Boolean, nullable=True, default=False)