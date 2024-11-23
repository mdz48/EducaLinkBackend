from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/educalink" educalink.cpo8mtxvyoqv.us-east-1.rds.amazonaws.com
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@educalink.cpo8mtxvyoqv.us-east-1.rds.amazonaws.com/educalink"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()