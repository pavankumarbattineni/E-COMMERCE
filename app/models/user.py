from sqlalchemy import Column, Integer, String, Boolean
from app.database.session import Base


#user model definition

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)  
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Integer, default=0, nullable=False)
    





