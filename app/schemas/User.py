from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

# Modelo base con los campos comunes
class UserBase(BaseModel):
    name: str
    lastname: str
    mail: EmailStr 
    user_type: str | None = "User"
    education_level: str
    state: str | None = "Activo"

    model_config = ConfigDict(from_attributes=True)

# Modelo para crear usuarios (sin id_user y con password)
class UserCreate(UserBase):
    password: str
    
    
class Token(BaseModel):
    access_token: str
    token_type: str

# Modelo para respuestas (con id_user pero sin password)
class UserResponse(UserBase):
    id_user: int
    creation_date: datetime

class TokenData(BaseModel):
    mail: str | None = None
    name: str | None = None
    lastname: str | None = None
    rol: str | None = None
