from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, Token, UserResponse
from app.auth.utils import get_user_by_email, create_access_token, get_current_user
from app.core.security import hash_password, verify_password
from app.database.db import get_db
from app.models.user import User
from datetime import timedelta
from app.core.config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# create a new router for authentication endpoints

router = APIRouter(prefix="/auth", tags=["Authentication"])

#register a new user

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):

    """Register a new user in the system.
    input : full_name: str, email: str, password: str, is_admin: int = 0
    output: UserResponse(id: int, full_name: str, email: str, is_admin: int)
    """

    try:
        db_user = get_user_by_email(db, user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_pwd = hash_password(user.password)
        new_user = User(
            email=user.email,
            hashed_password=hashed_pwd,
            is_admin=user.is_admin,
            full_name=user.full_name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# login an existing user

@router.post("/login", response_model=Token)
async def login(form_data: UserLogin, db: Session = Depends(get_db)):

    """Login an existing user and return an access token.
    input : email: str, password: str
    output: Token(access_token: str, token_type: str)"""

    try:
        user = get_user_by_email(db, form_data.email)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# get the current logged-in user from the token

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):

    """Get the current logged-in user.
    output: UserResponse(id: int, full_name: str, email: str, is_admin: int)"""

    try:
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user: {str(e)}")


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user. (Stateless - inform client to delete token)
    """
    return {"message": "Successfully logged out. Please delete the token on the client side."}
