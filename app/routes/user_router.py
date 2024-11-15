from fastapi import APIRouter, Depends, status, HTTPException, Security, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import jwt
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.models.Forum import Forum
from app.models.forum_posts import ForumPosts
from app.schemas.follower_schema import FollowerResponse
from app.schemas.forum_schema import ForumResponse
from app.schemas.post_schema import PostResponse
from app.shared.config.db import get_db
from app.models.User import Follower, User
from app.schemas.user_schema import UserCreate, UserResponse, Token
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Endpoint de login
@userRoutes.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
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
    token_data = {
        "id_user": user.id_user,
        "mail": user.mail,
        "name": user.name,
        "lastname": user.lastname,
        "education_level": user.education_level.name if user.education_level else None,
        "user_type": user.user_type,
        "state": user.state.name if user.state else None,
        "profile_image_url": user.profile_image_url,
        "background_image_url": user.background_image_url
    }
    
    # Añadir el token al encabezado de la respuesta
    response.headers["Authorization"] = f"Bearer {access_token}"
    
    return {"access_token": access_token, "token_type": "bearer", "token_data": token_data}

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

# Funcion para obtener los foros a los que pertenece un usuario
@userRoutes.get('/user/forums/{user_id}', status_code=status.HTTP_200_OK, response_model=List[ForumResponse])
async def get_forums_by_user(user_id: int, db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.id_forum.in_(db.query(UserForum.id_forum).filter(UserForum.id_user == user_id))).all()
    return forums
# Funcion para obtener los posts de un usuario
@userRoutes.get('/user/posts/{user_id}', status_code=status.HTTP_200_OK, response_model=List[PostResponse])
async def get_posts_by_user(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).join(User).all()
    return posts

# Funcion para seguir a un usuario
@userRoutes.post('/user/follow/{user_id}', status_code=status.HTTP_200_OK, response_model=FollowerResponse)
async def follow_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    follower = db.query(Follower).filter(Follower.id_user == user_id, Follower.follower_id == current_user.id_user).first()
    if user_id == current_user.id_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes seguir a ti mismo")
    if follower:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya seguido")
    new_follower = Follower(id_user=user_id, follower_id=current_user.id_user)
    db.add(new_follower)
    db.commit()
    db.refresh(new_follower)
    return new_follower  # This return should match FollowerResponse



# Funcion para obtener los seguidores de un usuario
@userRoutes.get('/user/followers/{id_user}', status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_followers_by_user(id_user: int, db: Session = Depends(get_db)):
    followers = db.query(Follower).filter(Follower.id_user == id_user).all()
    users = db.query(User).filter(User.id_user.in_(db.query(Follower.follower_id).filter(Follower.id_user == id_user))).all()
    return users

# Funcion para obtener los usuarios que un usuario sigue
@userRoutes.get('/user/following/{id_user}', status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_following_by_user(id_user: int, db: Session = Depends(get_db)):
    following = db.query(Follower).filter(Follower.follower_id == id_user).all()
    users = db.query(User).filter(User.id_user.in_(db.query(Follower.id_user).filter(Follower.follower_id == id_user))).all()
    return users



# Funcion para dejar de seguir a un usuario
@userRoutes.delete('/user/unfollow/{user_id}', status_code=status.HTTP_200_OK)
async def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    follower = db.query(Follower).filter(Follower.id_user == user_id, Follower.follower_id == current_user.id_user).first()
    if not follower:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no seguido")
    db.delete(follower)
    db.commit()
    return {"message": "Usuario dejado de seguir"}

# Funciona para actualizar un usuario
@userRoutes.put('/user/{user_id}', status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id_user == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    # Verificar que datos se quieren actualizar
    if user.name:
        db_user.name = user.name
    if user.lastname:
        db_user.lastname = user.lastname
    if user.mail:
        db_user.mail = user.mail
    if user.password:
        db_user.password = get_password_hash(user.password)
    if user.education_level:
        db_user.education_level = user.education_level
    if user.user_type:
        db_user.user_type = user.user_type
    if user.state:
        db_user.state = user.state
    if user.background_image_url:
        db_user.background_image_url = user.background_image_url
    if user.profile_image_url:
        db_user.profile_image_url = user.profile_image_url
        
    db.commit()
    db.refresh(db_user)
    return db_user
