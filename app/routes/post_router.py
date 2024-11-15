from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models.forum_posts import ForumPosts
from app.schemas.post_schema import PostCreate, PostResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user
from sqlalchemy import func
from app.models.comment import Comment
from app.models.user_forum import UserForum
from app.models.Forum import Forum
from app.models.User import User

postRoutes = APIRouter()

# Crear un nuevo post
@postRoutes.post('/post/', status_code=status.HTTP_201_CREATED, response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # ... validaciones previas ...
    db_post = ForumPosts(
        title=post.title,
        content=post.content,
        publication_date=datetime.now(),
        forum_id=post.forum_id,
        user_id=current_user.id_user
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)  # Refresca el objeto para obtener los datos actualizados
    return PostResponse(
        id_post=db_post.id_post,
        title=db_post.title,
        content=db_post.content,
        publication_date=db_post.publication_date,
        forum_id=db_post.forum_id,
        user=db_post.user,
        comment_count=0
    )

@postRoutes.get('/post/', response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    # Consulta los posts y carga la relación user
    posts = db.query(ForumPosts).options(joinedload(ForumPosts.user)).all()
    
    result = []
    for post in posts:
        # Cuenta el número de comentarios asociados al post
        comment_count = len(post.comments)
        
        # Crea la respuesta del post incluyendo el usuario
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=post.user,  # Aquí incluimos el objeto User
            comment_count=comment_count
        )
        result.append(post_response)
    return result


# Obtener un post por ID
@postRoutes.get('/post/{id_post}', response_model=PostResponse)
async def get_post_by_id(id_post: int, db: Session = Depends(get_db)):
    post = db.query(ForumPosts).options(joinedload(ForumPosts.user)).filter(ForumPosts.id_post == id_post).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    post_response = PostResponse(
        id_post=post.id_post,
        title=post.title,
        content=post.content,
        publication_date=post.publication_date,
        forum_id=post.forum_id,
        user=post.user,
        comment_count=len(post.comments)
    )
    return post_response


# Actualizar un post
@postRoutes.put('/post/{id_post}', response_model=PostResponse)
async def update_post(id_post: int, post: PostCreate, db: Session = Depends(get_db)):
    db_post = db.query(ForumPosts).filter(ForumPosts.id_post == id_post).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    db_post.title = post.title
    db_post.content = post.content
    db.commit()
    return db_post

# Eliminar un post
@postRoutes.delete('/post/{id_post}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id_post: int, db: Session = Depends(get_db)):
    db_post = db.query(ForumPosts).filter(ForumPosts.id_post == id_post).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    db.delete(db_post)
    db.commit()

# Obtener posts por ID de foro
@postRoutes.get('/posts/forum/{forum_id}', response_model=List[PostResponse])
async def get_posts_by_forum_id(forum_id: int, db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).options(joinedload(ForumPosts.user)).filter(ForumPosts.forum_id == forum_id).all()
    result = []
    for post in posts:
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=post.user,
            comment_count=len(post.comments)
        )
        result.append(post_response)
    return result


@postRoutes.get('/post/', response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(
        ForumPosts
    ).options(
        joinedload(ForumPosts.user)  # Carga la relación user de forma eficiente
    ).outerjoin(
        Comment,
        ForumPosts.id_post == Comment.post_id
    ).group_by(
        ForumPosts.id_post
    ).all()
    
    result = []
    for post in posts:
        comment_count = len(post.comments)
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=post.user,  # Aquí asignamos el objeto User directamente
            comment_count=comment_count
        )
        result.append(post_response)
    return result

