from fastapi import APIRouter, Depends, status, HTTPException, Security, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import jwt
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.models.Forum import Forum
from app.shared.config.db import get_db
from app.models.User import User
from app.schemas.user_schema import TokenData, UserCreate, UserResponse, Token
from app.models.user_forum import UserForum
from app.schemas.user_forum_schema import UserForumCreate, UserForumResponse
from app.shared.middlewares.security import (
    ALGORITHM,
    SECRET_KEY,
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

userRoutes = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

# Endpoint de login
@userRoutes.post("/login/", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print(form_data.username)
    user = db.query(User).filter(User.mail == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.mail}, expires_delta=access_token_expires
    )
    token_data = TokenData(
        mail=user.mail,
        name=user.name,
        lastname=user.lastname,
        education_level=user.education_level,
        user_type=user.user_type,
        state=user.state
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "token_data": token_data
    }

# Endpoint de registro modificado para hacer hash de la contraseña
@userRoutes.post('/user/', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el correo ya existe
    print(user)
    db_user = db.query(User).filter(User.mail == user.mail).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )
    
    # Crear usuario con contraseña hasheada
    hashed_password = get_password_hash(user.password)
    db_user = User(
        **user.model_dump(exclude={'password', 'creation_date'}),
        password=hashed_password,
        creation_date=datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Función para obtener el usuario actual
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mail: str = payload.get("sub")
        if mail is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.mail == mail).first()
    if user is None:
        raise credentials_exception
    return user

# Ejemplo de endpoint protegido
@userRoutes.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@userRoutes.get('/user/', response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    all_users = db.query(User).all()
    return all_users

# Funcion para obtener usuario por id
@userRoutes.get('/user/{user_id}', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id_user == user_id).first()
    return user

# Funcion para que el usuario se una a un foro
@userRoutes.post('/user/join_forum/{forum_id}', status_code=status.HTTP_200_OK, response_model=UserForumResponse)
async def join_forum(forum_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    forum = db.query(Forum).filter(Forum.id_forum == forum_id).first()
    if not forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    if db.query(UserForum).filter(UserForum.id_user == current_user.id_user, UserForum.id_forum == forum_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya pertenece al foro")
    user_forum = UserForum(
        id_user=current_user.id_user,
        id_forum=forum_id,
        join_date=datetime.now()
    )
    db.add(user_forum)
    db.commit()
    db.refresh(user_forum)
    return user_forum
