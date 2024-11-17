from fastapi import APIRouter, UploadFile, File, HTTPException
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

uploadRoutes = APIRouter()

@uploadRoutes.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    file_urls = []  # Lista para almacenar las URLs de los archivos subidos
    try:
        bucket_name = 'educalinkbucket'  # Reemplaza con tu nombre de bucket

        for file in files:
            file_key = f"{int(time.time())}_{file.filename}"  # Nombre único del archivo

            # Subir el archivo a S3
            s3.upload_fileobj(file.file, bucket_name, file_key, ExtraArgs={'ContentType': file.content_type})

            # Generar la URL del archivo subido
            file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
            file_urls.append(file_url)  # Agregar la URL a la lista

        return {"message": "Archivos subidos con éxito", "fileUrls": file_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo los archivos: {str(e)}") 