from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models.User import User
from app.models.ads import Ads
from app.schemas.ads_schema import AdsResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user

import boto3
import os
from dotenv import load_dotenv
import time

from app.shared.config.s3_files import upload_single_file_to_s3

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    aws_session_token=os.getenv("aws_session_token"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

adsRoutes = APIRouter()

# Crear una nueva publicidad
@adsRoutes.post('/ads/', status_code=status.HTTP_201_CREATED, response_model=AdsResponse, tags=["Publicidades"])
async def create_ads(
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...),
    link: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

# Verificamos que el usuario sea de tipo Admin
    if current_user.user_type != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para crear publicidades")

    # Subimos la imagen a S3
    file_key = f"{int(time.time())}_{image.filename}"
    s3.upload_fileobj(image.file, 'educalinkbucket', file_key, ExtraArgs={'ContentType': image.content_type})
    image_url = f"https://educalinkbucket.s3.us-east-1.amazonaws.com/{file_key}"
    if not image_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al subir la imagen a S3")
    
    # Creamos la publicidad
    new_ads = Ads(title=title, description=description, image_url=image_url, link=link, created_at=datetime.now())
    db.add(new_ads)
    db.commit()
    db.refresh(new_ads)
    return new_ads

# Obtener todas las publicidades
@adsRoutes.get('/ads/', response_model=List[AdsResponse], tags=["Publicidades"])
async def get_all_ads(db: Session = Depends(get_db)):
    ads = db.query(Ads).all()
    if not ads:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay publicidades registradas")
    return ads


# Eliminar una publicidad
@adsRoutes.delete('/ads/{id_ad}', status_code=status.HTTP_204_NO_CONTENT, tags=["Publicidades"])
async def delete_ads(id_ad: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ads = db.query(Ads).filter(Ads.id_ad == id_ad).first()
    if not ads:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicidad no encontrada")
    if current_user.user_type != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para eliminar publicidades")
    db.delete(ads)
    db.commit()
