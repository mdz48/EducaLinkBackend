from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models.User import User
from app.models.ads import Ads, Company
from app.models.files_model import Files
from app.schemas.ads_schema import AdsResponse
from app.shared.config.db import get_db
from app.routes.user_router import get_current_user
from app.schemas.company_schema import CompanyBase, CompanyResponse
from app.shared.config.s3_files import upload_single_file_to_s3


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


companyRoutes = APIRouter() 

# Creamos una empresa
@companyRoutes.post("/create", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED, tags=["Empresas"])
def create_company(
    name: str = Form(...),
    image_url: UploadFile = File(...),
    link: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):

    # Verificamos si el usuario es administrador
    if current_user.user_type != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para crear una empresa")
    # Verificamos si la empresa ya existe
    existing_company = db.query(Company).filter(Company.name == name).first()
    if existing_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La empresa ya existe")
    # Subimos la imagen a S3
    file_key = f"{int(time.time())}_{image_url.filename}"
    s3.upload_fileobj(image_url.file, 'educalinkbucket', file_key, ExtraArgs={'ContentType': image_url.content_type})
    image_url = f"https://educalinkbucket.s3.us-east-1.amazonaws.com/{file_key}"
    # Creamos la empresa
    new_company = Company(name=name, image_url=image_url, link=link)
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company

# Obtener todas las empresas
@companyRoutes.get('/companies/', response_model=List[CompanyResponse], tags=["Empresas"])
async def get_all_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    if not companies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay empresas")
    return companies
