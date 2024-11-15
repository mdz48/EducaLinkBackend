from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

# Modelo base con los campos comunes
class UserBase(BaseModel):
    name: str
    lastname: str
    mail: EmailStr 
    background_image_url: str | None = "https://drive.google.com/file/d/1CWU_gcEd4bxP4wgsggAioAqH_eSaroeu/view?usp=drive_link"
    profile_image_url: str | None = "https://drive.google.com/file/d/1pBinSzzha4-O1bJz8PZSX1ade_me5e6L/view?usp=drive_link"
    user_type: str | None = "User"
    education_level: str | None = "Preescolar"

    model_config = ConfigDict(from_attributes=True)

# Modelo para login (solo mail y password)
class UserLogin(BaseModel):
    mail: EmailStr
    password: str

# Modelo para crear usuarios (sin id_user y con password)
class UserCreate(UserBase):
    password: str
    state : str | None = "Activo"


# Modelo para respuestas (con id_user pero sin password)
class UserResponse(UserBase):
    id_user: int
    creation_date: datetime
    state: str | None = "Unknown"

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