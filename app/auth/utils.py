from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User
from app.auth.schemas import TokenData
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.security import pwd_context

#HTTP bearer security scheme for token authentication

security = HTTPBearer()

# generates jwt access tokenS

def create_access_token(data: dict, expires_delta: timedelta = None):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire, "sub": data.get("sub")})
        encoded_jwt =  jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
# get user by email from the database

def get_user_by_email(db: Session, email: str):
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

#get the current user from the token

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
        user = get_user_by_email(db, token_data.email)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")