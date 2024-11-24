from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models.files_model import Files
from app.models.forum_posts import ForumPosts
from app.schemas.post_schema import PostCreate, PostResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user
from sqlalchemy import func
from app.models.comment import Comment
from app.models.user_forum import UserForum
from app.models.Forum import Forum
from app.models.User import User
import boto3
import os
from dotenv import load_dotenv
import time

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    aws_session_token=os.getenv("aws_session_token"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)



postRoutes = APIRouter()

# Crear un nuevo post
@postRoutes.post('/post/', status_code=status.HTTP_201_CREATED, response_model=PostResponse, tags=["Posts"])
async def create_post(
    content: str = Form(...),
    title: str = Form(...),
    forum_id: int = Form(...),
    tag: str = Form(None),
    files: List[UploadFile] = File(None),  # Permitir archivos opcionales
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    db_post = ForumPosts(
        title=title,
        content=content,
        publication_date=datetime.now(),
        forum_id=forum_id,
        user_id=current_user.id_user,
        tag=tag
    )
    

    db.add(db_post)
    db.commit()
    db.refresh(db_post)  # Asegúrate de refrescar el objeto para obtener el id_post

    # Subir imágenes a S3 y guardar en la tabla post_files
    if files:
        for file in files:
            file_key = f"{int(time.time())}_{file.filename}"
            s3.upload_fileobj(file.file, 'educalinkbucket', file_key, ExtraArgs={'ContentType': file.content_type})
            file_url = f"https://educalinkbucket.s3.amazonaws.com/{file_key}"

            # Guardar la URL en la tabla post_files
            db_file = Files(post_id=db_post.id_post, url=file_url)
            db.add(db_file)
            # Verificar si hubo un error al subir el archivo
            if not db_file:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al subir el archivo")
            
    db.commit()  # Asegúrate de hacer commit después de agregar los archivos
    forum = db.query(Forum).filter(Forum.id_forum == forum_id).first()
    return PostResponse(
        id_post=db_post.id_post,
        title=db_post.title,
        content=db_post.content,
        publication_date=db_post.publication_date,
        forum_id=db_post.forum_id,
        user=db_post.user,
        comment_count=0,
        image_urls=[],  # Inicialmente vacío, puedes llenarlo al obtener el post
        forum=forum,
        tag=tag
    )

@postRoutes.get('/post/', response_model=List[PostResponse], tags=["Posts"])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).options(joinedload(ForumPosts.user)).all()
    
    result = []
    for post in posts:
        # Obtener las URLs de los archivos asociados
        file_urls = db.query(Files).filter(Files.post_id == post.id_post).all()
        urls = [file.url for file in file_urls]
        
        # Cuenta el número de comentarios asociados al post
        comment_count = len(post.comments)
        
        # Obtener el foro asociado al post
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
        
        # Obtener los tags asociados al post
        tag = post.tag
        
        # Crea la respuesta del post incluyendo el usuario, el foro y las URLs de las imágenes
        post_response = PostResponse(
            id_post=post.id_post, 
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=post.user,
            comment_count=comment_count,
            image_urls=urls,  # Incluir las URLs de las imágenes
            forum=forum,
            tag=tag
        )
        
        
        result.append(post_response)
    return result


# Obtener un post por ID
@postRoutes.get('/post/{id_post}', response_model=PostResponse, tags=["Posts"])
async def get_post_by_id(id_post: int, db: Session = Depends(get_db)):
    post = db.query(ForumPosts).options(joinedload(ForumPosts.user)).filter(ForumPosts.id_post == id_post).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")

    # Obtener las URLs de los archivos asociados
    file_urls = db.query(Files).filter(Files.post_id == id_post).all()
    urls = [file.url for file in file_urls]
    tag = post.tag
    forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
    post_response = PostResponse(
        id_post=post.id_post,
        title=post.title,
        content=post.content,
        publication_date=post.publication_date,
        forum_id=post.forum_id,
        user=post.user,
        comment_count=len(post.comments),
        forum=forum,
        image_urls=urls,  # Incluir las URLs de las imágenes
        tag=tag
    )
    return post_response


# Actualizar un post
@postRoutes.put('/post/{id_post}', response_model=PostResponse, tags=["Posts"])
async def update_post(id_post: int, post: PostCreate, db: Session = Depends(get_db)):
    db_post = db.query(ForumPosts).filter(ForumPosts.id_post == id_post).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    db_post.title = post.title
    db_post.content = post.content
    db.commit()
    return db_post

# Eliminar un post
@postRoutes.delete('/post/{id_post}', status_code=status.HTTP_204_NO_CONTENT, tags=["Posts"])
async def delete_post(id_post: int, db: Session = Depends(get_db)):
    db_post = db.query(ForumPosts).filter(ForumPosts.id_post == id_post).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    db.delete(db_post)
    db.commit()

# Obtener posts por ID de foro
@postRoutes.get('/posts/forum/{forum_id}', response_model=List[PostResponse], tags=["Posts"])
async def get_posts_by_forum_id(forum_id: int, db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).options(joinedload(ForumPosts.user)).filter(ForumPosts.forum_id == forum_id).all()
    result = []
    
    for post in posts:
        # Obtener las URLs de los archivos asociados
        file_urls = db.query(Files).filter(Files.post_id == post.id_post).all()
        urls = [file.url for file in file_urls]
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
        tag = post.tag
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=post.user,
            comment_count=len(post.comments),
            image_urls=urls,  # Incluir las URLs de las imágenes
            forum=forum,
            tag=tag
        )
        result.append(post_response)
    return result

# Obtener post por ID de foro excluyendo los posts del usuario actual
@postRoutes.get('/post/forum/{forum_id}/exclude/{user_id}', response_model=List[PostResponse], tags=["Posts"])
async def get_posts_by_forum_id_exclude_user(forum_id: int, user_id: int, db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).filter(ForumPosts.forum_id == forum_id, ForumPosts.user_id != user_id).all()
    result = []
    for post in posts:
        file_urls = db.query(Files).filter(Files.post_id == post.id_post).all()
        urls = [file.url for file in file_urls]
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
        tag = post.tag
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=post.user,
            comment_count=len(post.comments),
            forum=forum,
            image_urls=urls,
            tag=tag
        )
        result.append(post_response)
    return result

@postRoutes.get('/post/', response_model=List[PostResponse], tags=["Posts"])
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
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
        tag = post.tag
        comment_count = len(post.comments)
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=post.user,  # Aquí asignamos el objeto User directamente
            comment_count=comment_count,
            forum=forum,
            tag=tag
        )
        result.append(post_response)
    return result

# Obtener un post por user ID
@postRoutes.get('/post/user/{user_id}', response_model=List[PostResponse], tags=["Posts"])
async def get_post_by_user_id(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).options(joinedload(ForumPosts.user)).filter(ForumPosts.user_id == user_id).all()
    
    result = []
    for post in posts:
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()  # Obtener el foro
        tag = post.tag
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=post.user,
            comment_count=len(post.comments),
            forum=forum,  # Asegúrate de incluir el foro aquí
            image_urls=[],  # O cualquier otra lógica que necesites
            tag=tag
        )
        result.append(post_response)
    return result

# Obtener posts filtrados por rango de fechas de publicación
@postRoutes.get('/posts/filter', response_model=List[PostResponse], tags=["Posts"])
async def get_posts_filtered(start_date: datetime = None, end_date: datetime = None, db: Session = Depends(get_db)):
    query = db.query(ForumPosts).options(joinedload(ForumPosts.user))

    if start_date:
        query = query.filter(ForumPosts.publication_date >= start_date)
    if end_date:
        query = query.filter(ForumPosts.publication_date <= end_date)

    posts = query.all()
    
    result = []
    for post in posts:
        # Obtener las URLs de los archivos asociados
        file_urls = db.query(Files).filter(Files.post_id == post.id_post).all()
        urls = [file.url for file in file_urls]
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
        tag = post.tag
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=post.user,
            comment_count=len(post.comments),
            image_urls=urls,  # Incluir las URLs de las imágenes
            forum=forum,
            tag=tag
        )
        result.append(post_response)
    return result

# Obtener posts filtrados por tag
@postRoutes.get('/posts/tag/{tag}', response_model=List[PostResponse], tags=["Posts"])
async def get_posts_by_tag(tag: str, db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).filter(ForumPosts.tag == tag).all() 
    result = []
    for post in posts:
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
        user = db.query(User).filter(User.id_user == post.user_id).first()
        tag = post.tag
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=user,
            comment_count=len(post.comments),
            forum=forum,
            image_urls=[],
            tag=tag
        )
        result.append(post_response)
    return result

# Obtener los posts de un usuario donde el grupo sea publico
@postRoutes.get('/post/user/{user_id}/public', response_model=List[PostResponse], tags=["Posts"])
async def get_posts_by_user_id_public(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).filter(ForumPosts.user_id == user_id, ForumPosts.forum_id.in_(db.query(Forum.id_forum).filter(Forum.privacy == "Publico"))).all()
    result = []
    for post in posts:
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
        user = db.query(User).filter(User.id_user == post.user_id).first()
        tag = post.tag
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            forum_id=post.forum_id,
            publication_date=post.publication_date,
            user=user,
            comment_count=len(post.comments),
            forum=forum,
            image_urls=[],
            tag=tag
        )
        result.append(post_response)
    return result

# Funcion para obtener los posts de un usuario donde el grupo sea privado y el usuario actual pertenezca al grupo privado
@postRoutes.get('/post/user/{user_id}/private', response_model=List[PostResponse], tags=["Posts"])
async def get_posts_by_user_id_private(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: int = Depends(get_current_user)
):
    # Obtener los IDs de los foros privados donde el usuario actual es miembro
    private_forum_ids = db.query(UserForum.id_forum).filter(
        UserForum.id_user == current_user.id_user
    ).subquery()

    # Consulta para obtener posts que cumplan con alguna de estas condiciones:
    # 1. Posts en foros públicos
    # 2. Posts en foros privados donde el usuario actual es miembro
    posts = db.query(ForumPosts).join(
        Forum, ForumPosts.forum_id == Forum.id_forum
    ).filter(
        ForumPosts.user_id == user_id,
        (
            (Forum.privacy == "Publico") |  # Posts en foros públicos
            (
                (Forum.privacy == "Privado") &  # Posts en foros privados donde el usuario es miembro
                (Forum.id_forum.in_(private_forum_ids))
            )
        )
    ).all()

    result = []
    for post in posts:
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
        user = db.query(User).filter(User.id_user == post.user_id).first()
        tag = post.tag
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            forum_id=post.forum_id,
            publication_date=post.publication_date,
            user=user,
            comment_count=len(post.comments),
            forum=forum,
            image_urls=[],
            tag=tag
        )
        result.append(post_response)
    return result

# Funcion para obtener posts por un nombre parecido
@postRoutes.get('/post/search/{name}', status_code=status.HTTP_200_OK, response_model=List[PostResponse], tags=["Posts"])
async def get_posts_by_name(name: str, db: Session = Depends(get_db)):
    posts = db.query(ForumPosts).filter(ForumPosts.title.ilike(f"%{name}%")).all()
    result = []
    for post in posts:
        forum = db.query(Forum).filter(Forum.id_forum == post.forum_id).first()
        user = db.query(User).filter(User.id_user == post.user_id).first()
        tag = post.tag
        post_response = PostResponse(
            id_post=post.id_post,
            title=post.title,
            content=post.content,
            publication_date=post.publication_date,
            forum_id=post.forum_id,
            user=user,
            comment_count=len(post.comments),
            forum=forum,
            image_urls=[],
            tag=tag
        )
        result.append(post_response)
    return result 
