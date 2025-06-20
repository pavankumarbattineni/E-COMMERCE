
from fastapi import FastAPI
from app.auth.authenticate_router import router as auth_routes
from app.auth.category_router import router as category_routes
from app.auth.product_router import router as product_routes
from app.auth.order_router import router as order_routes

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

# Include the order management router with defined endpoints
app.include_router(order_routes)

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



"""

import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL")

st.set_page_config(page_title="🛒 E-Commerce App", layout="centered")

# Session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "refresh_categories" not in st.session_state:
    st.session_state.refresh_categories = True
if "refresh_products" not in st.session_state:
    st.session_state.refresh_products = True

# Sidebar navigation
menu = st.sidebar.radio("📍 Navigate", ["Register", "Login", "Profile", "Logout"])

# -------------------- Auth Utilities --------------------

def register_user(full_name, email, password, is_admin):
    return requests.post(
        f"{API_URL}/auth/register",
        json={"full_name": full_name, "email": email, "password": password, "is_admin": is_admin}
    )

def login_user(email, password):
    return requests.post(
        f"{API_URL}/auth/login",
        json={"email": email, "password": password}
    )

def get_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/auth/me", headers=headers)


# ---------------------- Pages ------------------------

if menu == "Register":
    st.title("📝 Register")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    is_admin = st.checkbox("Register as Admin", value=False)

    if st.button("Register"):
        if full_name and email and password:
            res = register_user(full_name, email, password, int(is_admin))
            if res.status_code == 200:
                st.success("✅ Registered successfully! You can now login.")
            else:
                st.error(f"❌ {res.json().get('detail')}")
        else:
            st.warning("⚠️ Please fill in all fields.")

elif menu == "Login":
    st.title("🔐 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if email and password:
            res = login_user(email, password)
            if res.status_code == 200:
                token = res.json()["access_token"]
                st.session_state.access_token = token
                st.success("✅ Logged in successfully!")
            else:
                st.error(f"❌ {res.json().get('detail')}")
        else:
            st.warning("⚠️ Please enter credentials.")

elif menu == "Profile":
    st.title("👤 Profile")
    if st.session_state.access_token:
        res = get_profile(st.session_state.access_token)
        if res.status_code == 200:
            user = res.json()
            st.session_state.user_info = user
            st.success("🔒 Authenticated")
            st.json(user)
        else:
            st.error("❌ Failed to fetch profile or token expired.")
    else:
        st.warning("🔑 Please login to view your profile.")


elif menu == "Logout":
    st.title("🔓 Logout")
    if st.session_state.access_token:
        st.session_state.access_token = None
        st.session_state.user_info = None
        st.success("✅ You have been logged out.")
    else:
        st.info("ℹ️ You are already logged out.")



this is existing streamlit add category and products 


"""
