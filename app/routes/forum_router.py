from datetime import datetime
from fastapi import APIRouter, Depends, Form, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from app.models.Forum import Forum, GroupType
from app.models.user_forum import UserForum
from app.models.User import User
from app.schemas.user_schema import UserResponse
from app.schemas.forum_schema import ForumCreate, ForumResponse, ForumResponseWithCreator
from app.schemas.user_forum_schema import UserForumResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user
from app.shared.middlewares.security import get_password_hash, verify_password
import boto3
import os
from dotenv import load_dotenv
import time

forumRoutes = APIRouter()

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    aws_session_token=os.getenv("aws_session_token"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# Crear un nuevo foro
@forumRoutes.post('/forum/', status_code=status.HTTP_201_CREATED, response_model=ForumResponseWithCreator, tags=["Foros"])
async def create_forum(
    name: str = Form(...),
    description: str = Form(...),
    privacy: GroupType = Form(...),
    password: str = Form(None),
    grade: int = Form(...),
    education_level: str = Form(...),
    image: UploadFile = File(None),
    background_image: UploadFile = File(None),
    db: Session = Depends(get_db), 
    current_user: int = Depends(get_current_user)
):
    forum = ForumCreate(
        name=name,
        description=description,
        privacy=privacy,
        password=password,
        grade=grade,
        education_level=education_level,
    )
    if privacy == GroupType.Privado and not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es obligatoria para foros privados"
        )
    
    hashed_password = get_password_hash(password) if password else None
    db_forum = Forum(
        **forum.model_dump(exclude={'creation_date', 'user_name', 'password'}),
        creation_date=datetime.now(),
        user_name=current_user.name,
        id_user=current_user.id_user,
        password=hashed_password
    )
    
    # if db_forum.background_image_url is None:
    #     db_forum.background_image_url = "https://educalinkbucket.s3.us-east-1.amazonaws.com/default_portrait_white.png"
    # if db_forum.image_url is None:
    #     db_forum.image_url = "https://educalinkbucket.s3.us-east-1.amazonaws.com/default_user.png"
        
    # Si se ingresaron imagenes entonces subirlas a S3
    if image:
        file_key = f"{int(time.time())}_{image.filename}"
        s3.upload_fileobj(image.file, 'educalinkbucket', file_key, ExtraArgs={'ContentType': image.content_type})
        db_forum.image_url = f"https://educalinkbucket.s3.us-east-1.amazonaws.com/{file_key}"
    else:
        db_forum.image_url = "https://educalinkbucket.s3.us-east-1.amazonaws.com/default_group.png"
    if background_image:
        file_key = f"{int(time.time())}_{background_image.filename}"
        s3.upload_fileobj(background_image.file, 'educalinkbucket', file_key, ExtraArgs={'ContentType': background_image.content_type})
        db_forum.background_image_url = f"https://educalinkbucket.s3.us-east-1.amazonaws.com/{file_key}"
    else:
        db_forum.background_image_url = "https://educalinkbucket.s3.us-east-1.amazonaws.com/default_portrait_white.png"
        
    db_forum.creator = current_user
    db.add(db_forum)
    db.commit()
    db.refresh(db_forum)
    
    # Unir al usuario al foro recién creado
    user_forum = UserForum(
        id_user=current_user.id_user,
        id_forum=db_forum.id_forum,
        join_date=datetime.now()
    )
    
    db.add(user_forum)
    db.commit()
    db.refresh(user_forum)

    return db_forum

# Obtener todos los foros
@forumRoutes.get('/forum/', response_model=List[ForumResponseWithCreator], tags=["Foros"])
async def get_forums(db: Session = Depends(get_db)):
    forums = db.query(Forum).all()
    for forum in forums:
        forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
        forum.users = db.query(User).join(UserForum, User.id_user == UserForum.id_user).filter(UserForum.id_forum == forum.id_forum).all()
        forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forums

# Obtener un foro por ID
@forumRoutes.get('/forum/{forum_id}', response_model=ForumResponseWithCreator, tags=["Foros"])
async def get_forum(forum_id: int, db: Session = Depends(get_db)):
    forum = db.query(Forum).filter(Forum.id_forum == forum_id).first()
    if not forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum_id).count()
    forum.users = db.query(User).join(UserForum, User.id_user == UserForum.id_user).filter(UserForum.id_forum == forum_id).all()
    forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forum

# Obtener un foro por nombre
@forumRoutes.get('/forum/name/{name}', response_model=ForumResponseWithCreator, tags=["Foros"])
async def get_forum_by_name(name: str, db: Session = Depends(get_db)):
    forum = db.query(Forum).filter(Forum.name == name).first()
    if not forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
    forum.users = db.query(User).join(UserForum, User.id_user == UserForum.id_user).filter(UserForum.id_forum == forum.id_forum).all()
    forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forum


# Actualizar un foro
@forumRoutes.put('/forum/{forum_id}', response_model=ForumResponseWithCreator, tags=["Foros"])
async def update_forum(
    forum_id: int, 
    name: str | None = Form(None),  # Cambiado a opcional
    description: str | None = Form(None),  # Cambiado a opcional
    password: str | None = Form(None),  # Cambiado a opcional
    education_level: str | None = Form(None),  # Cambiado a opcional
    grade: int | None = Form(None),  # Cambiado a opcional
    image: UploadFile | None = File(None),  # Cambiado a opcional
    background_image: UploadFile | None = File(None),  # Cambiado a opcional
    db: Session = Depends(get_db), 
    current_user: int = Depends(get_current_user)
):
    db_forum = db.query(Forum).filter(Forum.id_forum == forum_id).first()
    if not db_forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    
    # La privacidad no se puede cambiar
    privacy = db_forum.privacy
    
    # Actualizar solo los campos que se proporcionan
    if name is not None:
        db_forum.name = name
    if description is not None:
        db_forum.description = description
    if password is not None and privacy == GroupType.Privado:
        db_forum.password = get_password_hash(password)
    if education_level is not None:
        db_forum.education_level = education_level
    if grade is not None:
        db_forum.grade = grade
    if image:
        file_key = f"{int(time.time())}_{image.filename}"
        s3.upload_fileobj(image.file, 'educalinkbucket', file_key, ExtraArgs={'ContentType': image.content_type})
        db_forum.image_url = f"https://educalinkbucket.s3.us-east-1.amazonaws.com/{file_key}"
    else:
        db_forum.image_url = db_forum.image_url
    if background_image:
        file_key = f"{int(time.time())}_{background_image.filename}"
        s3.upload_fileobj(background_image.file, 'educalinkbucket', file_key, ExtraArgs={'ContentType': background_image.content_type})
        db_forum.background_image_url = f"https://educalinkbucket.s3.us-east-1.amazonaws.com/{file_key}"
    else:
        db_forum.background_image_url = db_forum.background_image_url
    db_forum.privacy = privacy
    db.commit()
    db.refresh(db_forum)

    # Agregar el creador a la respuesta
    db_forum.creator = db.query(User).filter(User.id_user == db_forum.id_user).first()

    return db_forum

# Eliminar un foro
@forumRoutes.delete('/forum/{forum_id}', status_code=status.HTTP_204_NO_CONTENT, tags=["Foros"])
async def delete_forum(forum_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_forum = db.query(Forum).filter(Forum.id_forum == forum_id).first()
    if not db_forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
        
    db.delete(db_forum)
    db.commit()
    return

# Funcion para obtener todos los usuarios de un foro
@forumRoutes.get('/forum/{forum_id}/users', status_code=status.HTTP_200_OK, response_model=List[UserResponse], tags=["Foros"])
async def get_users_by_forum(forum_id: int, db: Session = Depends(get_db)):
    if not db.query(Forum).filter(Forum.id_forum == forum_id).first(): 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    users = db.query(User).join(UserForum, User.id_user == UserForum.id_user).filter(UserForum.id_forum == forum_id).all()
    return users

# Funcion para obtener los foros en base a education_level
@forumRoutes.get('/forum/education_level/{education_level}', status_code=status.HTTP_200_OK, response_model=List[ForumResponse], tags=["Foros"])
async def get_forums_by_education_level(education_level: str, db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.education_level == education_level).all()
    for forum in forums:
        forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
        forum.users = db.query(User).join(UserForum, User.id_user == UserForum.id_user).filter(UserForum.id_forum == forum.id_forum).all()
        forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forums

# Funcion para obtener un foro por nombre
@forumRoutes.get('/forum/name/{name}', status_code=status.HTTP_200_OK, response_model=ForumResponse, tags=["Foros"])
async def get_forum_by_name(name: str, db: Session = Depends(get_db)):
    forum = db.query(Forum).filter(Forum.name == name).first()
    if not forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
    forum.users = db.query(User).join(UserForum, User.id_user == UserForum.id_user).filter(UserForum.id_forum == forum.id_forum).all()
    forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forum  

# Funcion para unir un usuario a un foro
@forumRoutes.post('/forum/{forum_id}/join', status_code=status.HTTP_200_OK, tags=["Foros"])
async def join_forum(forum_id: int, password: str | None = '', db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_forum = db.query(Forum).filter(Forum.id_forum == forum_id).first()
    if not db_forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    
    if db_forum.privacy == GroupType.Privado and db_forum.password:
        if not verify_password(password, db_forum.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")
    if db.query(UserForum).filter(UserForum.id_user == current_user.id_user, UserForum.id_forum == forum_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya pertenece al foro")
    
    user_forum = UserForum(
        id_user=current_user.id_user,
        id_forum=db_forum.id_forum,
        join_date=datetime.now()
    )
    db.add(user_forum)
    db.commit()
    db.refresh(user_forum)
    return user_forum

# Funcion para salir de un foro (duplicado en user_router, lo quiero ordenar)
@forumRoutes.delete('/forum/{forum_id}/leave', status_code=status.HTTP_204_NO_CONTENT, tags=["Foros"])
async def leave_forum(user_id: int, forum_id: int, db: Session = Depends(get_db)):
    user_forum = db.query(UserForum).filter(UserForum.id_user == user_id, UserForum.id_forum == forum_id).first()
    if not user_forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no pertenece al foro")
    # Verificar que el usuario tenga al menos un foro
    if db.query(UserForum).filter(UserForum.id_user == user_id).count() == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario debe pertenecer a al menos un foro")
    db.delete(user_forum)
    db.commit()
    return

# Funcion para obtener todos los foros de un usuario (duplicado en user_router, lo quiero ordenar x2)
@forumRoutes.get('/forum/user/{user_id}', status_code=status.HTTP_200_OK, response_model=List[ForumResponseWithCreator], tags=["Foros"])
async def get_forums_by_user(user_id: int, db: Session = Depends(get_db)):
    forums = db.query(Forum).join(UserForum, Forum.id_forum == UserForum.id_forum).filter(UserForum.id_user == user_id).all()
    for forum in forums:
        forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
        # forum.users = db.query(User).join(UserForum, User.id_user == UserForum.id_user).filter(UserForum.id_forum == forum.id_forum).all()
        forum.creator = db.query(User).filter(User.id_user == forum.id_user).first() 
    forums.sort(key=lambda x: x.users_count, reverse=True)
    return forums

# Filtrar foros por grade
@forumRoutes.get('/forum/grade/{grade}', status_code=status.HTTP_200_OK, response_model=List[ForumResponse], tags=["Foros"])
async def get_forums_by_grade(grade: int, db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.grade == grade).all()
    for forum in forums:
        forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
        forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forums

# Filtrar foros por grado y educación
@forumRoutes.get('/forum/grade/{grade}/education_level/{education_level}', status_code=status.HTTP_200_OK, response_model=List[ForumResponse], tags=["Foros"])
async def get_forums_by_grade_and_education_level(grade: int, education_level: str, db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.grade == grade, Forum.education_level == education_level).all()
    for forum in forums:
        forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
        forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forums

# Funcion para obtener los foros en los que el usuario no pertenece y ademas esta filtrado por grade y education_level
@forumRoutes.get('/forum/user/{user_id}/not_in/{grade}/{education_level}', status_code=status.HTTP_200_OK, response_model=List[ForumResponse], tags=["Foros"])
async def get_forums_by_user_not_in_grade_and_education_level(user_id: int, grade: int, education_level: str, db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.grade == grade, Forum.education_level == education_level, Forum.id_forum.notin_(db.query(UserForum.id_forum).filter(UserForum.id_user == user_id))).all()
    for forum in forums:
        forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
        forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forums

# Funcion para obtener los foros en los que el usuario no pertenece y ademas esta filtrado education_level
@forumRoutes.get('/forum/user/{user_id}/not_in/{education_level}', status_code=status.HTTP_200_OK, response_model=List[ForumResponse], tags=["Foros"])
async def get_forums_by_user_not_in_education_level(user_id: int, education_level: str, db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.education_level == education_level, Forum.id_forum.notin_(db.query(UserForum.id_forum).filter(UserForum.id_user == user_id))).all()
    for forum in forums:
        forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
        forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forums

# Funcion para obtener los foros en los que el usuario no pertenece 
@forumRoutes.get('/forum/user/{user_id}/not_in', status_code=status.HTTP_200_OK, response_model=List[ForumResponse], tags=["Foros"])
async def get_forums_by_user_not_in(user_id: int, db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.id_forum.notin_(db.query(UserForum.id_forum).filter(UserForum.id_user == user_id))).all()
    for forum in forums:
        forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
        forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forums

# Funcion para obtener los foros por un nombre parecido
@forumRoutes.get('/forum/search/{name}', status_code=status.HTTP_200_OK, response_model=List[ForumResponse], tags=["Foros"])
async def get_forums_by_name(name: str, db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(Forum.name.ilike(f"%{name}%")).all()
    for forum in forums:
        forum.users_count = db.query(UserForum).filter(UserForum.id_forum == forum.id_forum).count()
        forum.creator = db.query(User).filter(User.id_user == forum.id_user).first()
    return forums