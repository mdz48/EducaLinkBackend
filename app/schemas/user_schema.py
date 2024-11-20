from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional

# Modelo base con los campos comunes
class UserBase(BaseModel):
    name: str
    lastname: str
    mail: EmailStr 
    background_image_url: str | None = "https://educalinkbucket.s3.us-east-1.amazonaws.com/default_portrait_white.png"
    profile_image_url: str | None = "https://educalinkbucket.s3.us-east-1.amazonaws.com/default_user.png"
    grade: int | None = 1
    user_type: str | None = "User"
    education_level: str | None = "Preescolar"
    state: str | None = "Activo"

    model_config = ConfigDict(from_attributes=True)

# Modelo para login (solo mail y password)
class UserLogin(BaseModel):
    mail: EmailStr
    password: str

# Modelo para crear usuarios (sin id_user y con password)
class UserCreate(UserBase):
    password: str
    


# Modelo para respuestas (con id_user pero sin password)
class UserResponse(UserBase):
    id_user: int
    creation_date: datetime

class TokenData(BaseModel):
    id_user : int | None = None
    mail: str | None = None
    name: str | None = None
    lastname: str | None = None
    education_level: str | None = None
    user_type: str | None = None
    state: str | None = None
    profile_image_url: str | None = None
    background_image_url: str | None = None

    
class Token(BaseModel):
    access_token: str
    token_type: str
    token_data: TokenData