from passlib.context import CryptContext
from fastapi import HTTPException

#password hashing context using bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#hash and verify password functions

def hash_password(password: str):
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password hashing failed: {str(e)}")

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password verification failed: {str(e)}")