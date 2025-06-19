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
