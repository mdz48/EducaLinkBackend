
# Step 1: Import necessary modules
import time
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

def upload_single_file_to_s3(file, educalinkbucket):
    
    file_key = f"{int(time.time())}_{file.filename}"
    
    s3.upload_fileobj(file, educalinkbucket, file_key, ExtraArgs={'ContentType': file.content_type})
    return f"https://educalinkbucket.s3.amazonaws.com/{file_key}"

def upload_multiple_files_to_s3(files, educalinkbucket):
    for file in files:
        file_key = f"{int(time.time())}_{file.filename}"
        s3.upload_fileobj(file, educalinkbucket, file_key, ExtraArgs={'ContentType': file.content_type})
        return f"https://educalinkbucket.s3.amazonaws.com/{file_key}"



