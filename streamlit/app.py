import streamlit as st
import requests
import os
from dotenv import load_dotenv

# -------- Load Environment Variables -------- #
load_dotenv()
API_URL = os.getenv("API_URL")

st.set_page_config(page_title="🛒 E-Commerce Auth", layout="centered")

# -------- Utility functions -------- #
def register_user(email, password, full_name, is_admin):
    try:
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
    except requests.exceptions.ConnectionError:
        st.error("🔌 Could not connect to the server. Please try again later.")
    except requests.exceptions.Timeout:
        st.error("⏳ The server took too long to respond.")
    except Exception:
        st.error("🚫 An unexpected error occurred during registration.")
    return None

def login_user(email, password):
    try:
        response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Could not connect to the server. Please check your connection.")
    except requests.exceptions.Timeout:
        st.error("⏳ Login request timed out.")
    except Exception:
        st.error("🚫 An unexpected error occurred while trying to log in.")
    return None

def get_user_profile(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/me", headers=headers)
        return response
    except requests.exceptions.ConnectionError:
        st.error("🔌 Unable to reach the server. Please ensure it's running.")
    except requests.exceptions.Timeout:
        st.error("⏳ Request timed out while fetching profile.")
    except Exception:
        st.error("🚫 Something went wrong while fetching your profile.")
    return None

# -------- UI -------- #
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
            st.warning("⚠️ Full name is required.")
        elif not email:
            st.warning("⚠️ Email is required.")
        elif not password:
            st.warning("⚠️ Password is required.")
        elif len(password) < 8:
            st.warning("⚠️ Password must be at least 8 characters long.")
        else:
            response = register_user(email, password, full_name, is_admin)
            if response:
                if response.status_code == 200:
                    st.success("✅ Registration successful. You can now log in.")
                else:
                    try:
                        detail = response.json().get("detail", "Unknown error occurred.")
                        st.error(f"❌ {detail}")
                    except:
                        st.error("❌ Registration failed. Please try again.")
            else:
                st.warning("⚠️ Registration could not be completed.")

elif page == "Login":
    st.header("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not email:
            st.warning("⚠️ Email is required.")
        elif not password:
            st.warning("⚠️ Password is required.")
        else:
            user_data = login_user(email, password)
            if user_data:
                try:
                    st.session_state["token"] = user_data["access_token"]
                    st.success("✅ Logged in successfully.")
                except KeyError:
                    st.error("❌ Login succeeded but token is missing. Please try again.")
            else:
                st.error("❌ Invalid credentials or login failed. Please try again.")

elif page == "Profile":
    st.header("Your Profile")
    token = st.session_state.get("token")
    if token:
        response = get_user_profile(token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    st.write(f"📧 Email: {data['email']}")
                    st.write(f"🙍 Full Name: {data.get('full_name', 'N/A')}")
                    st.write(f"🆔 ID: {data['id']}")
                    st.write(f"🔐 Role: {'Admin' if data.get('is_admin') else 'User'}")
                except:
                    st.error("❌ Failed to read profile information.")
            else:
                st.warning("⚠️ Session expired or token is invalid. Please login again.")
        else:
            st.warning("⚠️ Unable to fetch profile details.")
    else:
        st.info("🔐 Please login to view your profile.")
