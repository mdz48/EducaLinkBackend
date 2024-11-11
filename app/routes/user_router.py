from fastapi import APIRouter, Depends, status, HTTPException, Security, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import jwt
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.models.Forum import Forum
from app.models.forum_posts import ForumPosts
from app.schemas.forum_schema import ForumResponse
from app.schemas.post_schema import PostResponse
from app.shared.config.db import get_db
from app.models.User import User
from app.schemas.user_schema import TokenData, UserCreate, UserResponse, Token, UserLogin
from app.models.user_forum import UserForum
from app.schemas.user_forum_schema import UserForumCreate, UserForumResponse
from fastapi.responses import JSONResponse
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
@userRoutes.post("/login/", response_model=UserResponse)
async def login_for_access_token(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    user_db = db.query(User).filter(User.mail == user.mail).first()
    if not user_db or not verify_password(user.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_db.mail}, expires_delta=access_token_expires
    )

    headers = {"Authorization": f"Bearer {access_token}"}

    # Convertir valores de Enum a string con `.value`
    user_data = {
        "id_user": user_db.id_user,
        "name": user_db.name,
        "lastname": user_db.lastname,
        "mail": user_db.mail,
        "background_image_url": user_db.background_image_url,
        "profile_image_url": user_db.profile_image_url,
        "user_type": user_db.user_type,
        "education_level": user_db.education_level.value if user_db.education_level else None,
        "creation_date": user_db.creation_date.isoformat(),
        "state": user_db.state.value if user_db.state else None
    }

    return JSONResponse(content=user_data, headers=headers, status_code=status.HTTP_200_OK)



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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya pertenece al foro")
    user_forum = UserForum(
        id_user=current_user.id_user,
        id_forum=forum_id,
        join_date=datetime.now()
    )
    db.add(user_forum)
    db.commit()
    db.refresh(user_forum)
    return user_forum

# Funcion para obtener los foros a los que pertenece un usuario
@userRoutes.get('/user/forums/{user_id}', status_code=status.HTTP_200_OK, response_model=List[ForumResponse])
async def get_forums_by_user(user_id: int, db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.id_forum.in_(db.query(UserForum.id_forum).filter(UserForum.id_user == user_id))).all()
    return forums

# Funcion para obtener los posts de un usuario
@userRoutes.get('/user/posts/{user_id}', status_code=status.HTTP_200_OK, response_model=List[PostResponse])
async def get_posts_by_user(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).filter(ForumPosts.user_id == user_id).all()
    return posts

