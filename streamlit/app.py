import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL")

st.set_page_config(page_title="🛒 E-Commerce Auth", layout="centered")

# Utility Functions
def register_user(email, password, full_name, is_admin):
    response = requests.post(
        f"{API_URL}/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
            "is_admin": is_admin
        }
    )
    return response

def login_user(email, password):
    response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
    return response.json() if response.status_code == 200 else None

def get_user_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/me", headers=headers)

# UI
st.title("🛍️ E-Commerce - Auth System")
page = st.sidebar.radio("Navigate", ["Register", "Login", "Profile"])

if page == "Register":
    st.header("Register New User")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.radio("Role", ["User", "Admin"])
    is_admin = 1 if role == "Admin" else 0

    if st.button("Register"):
        if not full_name:
            st.warning("Full name is required.")
        elif not email:
            st.warning("Email is required.")
        elif not password:
            st.warning("Password is required.")
        elif len(password) < 8:
            st.warning("Password must be at least 8 characters long.")
        else:
            try:
                response = register_user(email, password, full_name, is_admin)
                if response.status_code == 200:
                    st.success("✅ Registration successful. You can now log in.")
                else:
                    st.error(f"❌ {response.json().get('detail', 'Registration failed.')}")
            except Exception as e:
                st.error("Something went wrong during registration.")

elif page == "Login":
    st.header("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email:
            st.warning("Email is required.")
        elif not password:
            st.warning("Password is required.")
        else:
            try:
                user_data = login_user(email, password)
                if user_data:
                    st.session_state["token"] = user_data["access_token"]
                    st.success("✅ Logged in successfully.")
                else:
                    st.error("❌ Invalid credentials or login failed.")
            except Exception:
                st.error("Something went wrong during login.")

elif page == "Profile":
    st.header("Your Profile")
    token = st.session_state.get("token")

    if token:
        try:
            response = get_user_profile(token)
            if response.status_code == 200:
                data = response.json()
                st.write(f"📧 Email: {data['email']}")
                st.write(f"🙍 Full Name: {data.get('full_name', 'N/A')}")
                st.write(f"🆔 ID: {data['id']}")
                st.write(f"🔐 Role: {'Admin' if data.get('is_admin') else 'User'}")
            else:
                st.warning("Session expired or token invalid.")
        except Exception:
            st.error("Failed to load profile.")
    else:
        st.info("Please login to view your profile.")
