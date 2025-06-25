from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User
from app.core.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

# HTTP bearer security scheme for token authentication
security = HTTPBearer()

# Generates JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None):

    """Create a JWT access token with the provided data and expiration time.
    If expires_delta is not provided, it defaults to 15 minutes.
    The token includes the expiration time and the subject (user email) in its payload.
    If an error occurs during token creation, it raises an HTTPException with a 500 status code."""
    
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire, "sub": data.get("sub")})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Get user by email from the database
def get_user_by_email(db: Session, email: str):
    
    return db.query(User).filter(User.email == email).first()
    

# Get the current user from the token
from jose import jwt, JWTError, ExpiredSignatureError

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    
    """Get the current user based on the provided JWT token.
    This function decodes the JWT token, retrieves the user email from the payload,
    and fetches the user from the database.
    If the token is invalid or expired, it raises an HTTPException."""
    try:
        payload = jwt.decode(
            token.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],  
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except JWTError as e:
        raise HTTPException(status_code=403, detail=f"Invalid token: {str(e)}")

# Check if the current user is an admin
def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user




