from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.Forum import Forum, GroupType
from app.models.user_forum import UserForum
from app.schemas.User import UserResponse
from app.schemas.forum_schema import ForumCreate, ForumResponse
from app.schemas.user_forum_schema import UserForumResponse
from app.shared.config.db import get_db
from app.routes.userRouter import get_current_user

forumRoutes = APIRouter()

# Crear un nuevo foro
@forumRoutes.post('/forum/', status_code=status.HTTP_201_CREATED, response_model=ForumResponse)
async def create_forum(forum: ForumCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    if forum.privacy == GroupType.Private and not forum.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es obligatoria para foros privados"
        )
    
    db_forum = Forum(
        **forum.model_dump(exclude={'creation_date'}),
        creation_date=datetime.now(),
        id_user=current_user.id_user
    )
    db.add(db_forum)
    db.commit()
    db.refresh(db_forum)
    return db_forum

# Obtener todos los foros
@forumRoutes.get('/forum/', response_model=List[ForumResponse])
async def get_forums(db: Session = Depends(get_db)):
    forums = db.query(Forum).all()
    return forums

# Obtener un foro por ID
@forumRoutes.get('/forum/{forum_id}', response_model=ForumResponse)
async def get_forum(forum_id: int, db: Session = Depends(get_db)):
    forum = db.query(Forum).filter(Forum.id_forum == forum_id).first()
    if not forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    return forum

# Actualizar un foro
@forumRoutes.put('/forum/{forum_id}', response_model=ForumResponse)
async def update_forum(forum_id: int, forum: ForumCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_forum = db.query(Forum).filter(Forum.id_forum == forum_id).first()
    if not db_forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    
    if forum.privacy == GroupType.Private and not forum.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es obligatoria para foros privados"
        )
    
    for key, value in forum.model_dump(exclude={'creation_date'}).items():
        setattr(db_forum, key, value)
    
    db.commit()
    db.refresh(db_forum)
    return db_forum

# Eliminar un foro
@forumRoutes.delete('/forum/{forum_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_forum(forum_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_forum = db.query(Forum).filter(Forum.id_forum == forum_id).first()
    if not db_forum:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    
    db.delete(db_forum)
    db.commit()
    return

# Funcion para obtener todos los usuarios de un foro
@forumRoutes.get('/forum/{forum_id}/users', status_code=status.HTTP_200_OK, response_model=List[UserForumResponse])
async def get_users_by_forum(forum_id: int, db: Session = Depends(get_db)):
    users = db.query(UserForum).filter(UserForum.id_forum == forum_id).all()
    return users