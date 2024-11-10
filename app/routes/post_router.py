from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
    if db.query(Forum).filter(Forum.id_forum == post.forum_id).first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foro no encontrado")
    if db.query(User).filter(User.id_user == current_user.id_user).first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if db.query(UserForum).filter(UserForum.id_forum == post.forum_id).filter(UserForum.id_user == current_user.id_user).first() is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no pertenece a este foro")
    db_post = ForumPosts(
        **post.model_dump(exclude={'publication_date', 'user_id', 'user_name', 'user_profile_image_url', 'user_education_level'}),
        publication_date=datetime.now(),
        user_id=current_user.id_user,
        user_name=current_user.name,
        user_profile_image_url=current_user.profile_image_url,
        user_education_level=current_user.education_level
    )
    print(db_post.user_id, db_post.user_name, db_post.user_profile_image_url, db_post.content, db_post.forum_id)
    db.add(db_post)
    db.commit()
    return db_post

@postRoutes.get('/post/', response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(
        ForumPosts,
        func.count(Comment.id_comment).label('comment_count')
    ).outerjoin(
        Comment,
        ForumPosts.id_post == Comment.post_id
    ).group_by(
        ForumPosts.id_post
    ).all()
    
    # Convertir los resultados al formato esperado
    return [
        {
            **post[0].__dict__,
            'comment_count': post[1]
        }
        for post in posts
    ]

# Obtener un post por ID
@postRoutes.get('/post/{id_post}', response_model=PostResponse)
async def get_post_by_id(id_post: int, db: Session = Depends(get_db)):
    post = db.query(ForumPosts).filter(ForumPosts.id_post == id_post).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    return post

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
    posts = db.query(ForumPosts).filter(ForumPosts.forum_id == forum_id).all()
    return posts

