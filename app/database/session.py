from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings    

# Create  database engine 
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)

#create a configured "Session" class

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models

Base = declarative_base()

