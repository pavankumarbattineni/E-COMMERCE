
from fastapi import FastAPI
from app.auth.authenticate_router import router as auth_routes
from app.auth.category_router import router as category_routes
from app.auth.product_router import router as product_routes


from app.database.session import Base, engine

# Create all tables in the database (from models)

Base.metadata.create_all(bind=engine)

# Initialize FastAPI application

app = FastAPI()

# Include the auth router with defined endpoints

app.include_router(auth_routes)

# Include the category management router with defined endpoints
app.include_router(category_routes)

# Include the product management router with defined endpoints
app.include_router(product_routes)

# Define a simple home route
@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce API"}



"""1. emily.thompson829@gmail.com | Password: R#t9uV!e2kLp  
2. jacob.wilson473@gmail.com   | Password: Mz8@Ye4$pQx1  
3. sophie.martin912@gmail.com  | Password: sophie@123"""























"""from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database.db import Base, engine, SessionLocal
from database.models import User


#---------------------------------CONFIG---------------------------------

SECRET_KEY = "620a8070e7d8b4d69349c7591be635ce03654fb010537c7296e2e186d1cbd5c8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 27

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
security = HTTPBearer()

#---------------------------------Create TAbles----------------------------

Base.metadata.create_all(bind = engine)

#---------------------------SCHEMAS(PYDANTIC) -----------------------------

class UserCreate(BaseModel):
    email : EmailStr
    password : str = Field(..., min_length = 8)

class UserLogin(BaseModel):
    email : EmailStr
    password : str = Field(..., min_length=8)

class Token(BaseModel):
    access_token : str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    
    model_config = {
        "from_attributes": True
    }

#-----------------------------UTILITY FUNCTIONS-----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()



async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
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
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception
    return user

# -------------------------- ROUTES(END-POINTS) ----------------------------------

@app.post("/register", response_model=UserCreate)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@app.post("/login", response_model=Token)
def login(form_data : UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", }

@app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce API"}



"""