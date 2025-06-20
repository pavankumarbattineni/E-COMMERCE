# redesigned_ecommerce_app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL")

st.set_page_config(page_title="🛒 E-Commerce App", layout="wide")

# Session state setup
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

def auth_header():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

# API Utility Functions

def register_user(full_name, email, password, is_admin):
    return requests.post(f"{API_URL}/auth/register", json={
        "full_name": full_name, "email": email,
        "password": password, "is_admin": is_admin
    })

def login_user(email, password):
    return requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})

def get_profile():
    return requests.get(f"{API_URL}/auth/me", headers=auth_header())

def fetch_categories():
    return requests.get(f"{API_URL}/categories/")

def fetch_products():
    return requests.get(f"{API_URL}/products/")

def create_category(data):
    return requests.post(f"{API_URL}/categories/", json=data, headers=auth_header())

def update_category(cat_id, data):
    return requests.put(f"{API_URL}/categories/{cat_id}", json=data, headers=auth_header())

def delete_category(cat_id):
    return requests.delete(f"{API_URL}/categories/{cat_id}", headers=auth_header())

def create_product(data):
    return requests.post(f"{API_URL}/products/", json=data, headers=auth_header())

def update_product(prod_id, data):
    return requests.put(f"{API_URL}/products/{prod_id}", json=data, headers=auth_header())

def delete_product(prod_id):
    return requests.delete(f"{API_URL}/products/{prod_id}", headers=auth_header())

# Auth Pages
if not st.session_state.access_token:
    auth_tab = st.sidebar.radio("Authentication", ["Login", "Register"])
    
    if auth_tab == "Login":
        st.title("🔐 Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            res = login_user(email, password)
            if res.status_code == 200:
                token = res.json()["access_token"]
                st.session_state.access_token = token
                user = get_profile().json()
                st.session_state.user_info = user
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error(res.json().get("detail"))

    elif auth_tab == "Register":
        st.title("📝 Register")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pwd")
        is_admin = st.checkbox("Register as Admin")
        if st.button("Register"):
            res = register_user(full_name, email, password, int(is_admin))
            if res.status_code == 200:
                st.success("✅ Registered. Please login.")
            else:
                st.error(res.json().get("detail"))

else:
    # Authenticated UI
    user = st.session_state.user_info
    st.sidebar.markdown(f"👤 Welcome, **{user['full_name']}**")
    menu = st.sidebar.radio("Menu", ["Profile", "Categories", "Products", "Logout"])

    if menu == "Profile":
        st.title("👤 Profile")
        st.json(user)

    elif menu == "Categories":
        st.title("📂 Categories")
        cat_res = fetch_categories()
        if cat_res.status_code == 200:
            categories = cat_res.json()
        else:
            st.error("Failed to load categories")
            categories = []

        cat_tab = st.tabs(["View", "Add", "Update", "Delete"])

        with cat_tab[0]:
            st.subheader("📋 All Categories")
            for c in categories:
                st.markdown(f"### {c['name']}")
                st.write(c['description'])
                if c.get("image_url"):
                    st.image(c["image_url"], width=300)

        if user["is_admin"]:
            with cat_tab[1]:
                st.subheader("➕ Add Category")
                name = st.text_input("Category Name")
                desc = st.text_area("Description")
                img = st.text_input("Image URL")
                if st.button("Create Category"):
                    res = create_category({"name": name, "description": desc, "image_url": img})
                    if res.status_code == 200:
                        st.success("✅ Created")
                    else:
                        st.error(res.json().get("detail"))

            with cat_tab[2]:
                st.subheader("✏️ Update Category")
                cat_map = {f"{c['name']} (ID:{c['id']})": c for c in categories}
                choice = st.selectbox("Select", list(cat_map.keys()))
                cat = cat_map[choice]
                new_name = st.text_input("Name", value=cat["name"])
                new_desc = st.text_area("Description", value=cat["description"])
                new_img = st.text_input("Image URL", value=cat["image_url"])
                if st.button("Update"):
                    res = update_category(cat["id"], {"name": new_name, "description": new_desc, "image_url": new_img})
                    if res.status_code == 200:
                        st.success("✅ Updated")

            with cat_tab[3]:
                st.subheader("🗑️ Delete Category")
                del_choice = st.selectbox("Select", list(cat_map.keys()), key="delcat")
                del_id = cat_map[del_choice]["id"]
                if st.button("Delete Category"):
                    res = delete_category(del_id)
                    if res.status_code == 200:
                        st.success("✅ Deleted")

    elif menu == "Products":
        st.title("🛍️ Products")

        # Fetch categories and products
        cat_res = fetch_categories()
        prod_res = fetch_products()
        if cat_res.status_code == 200 and prod_res.status_code == 200:
            categories = cat_res.json()
            products = prod_res.json()
        else:
            st.error("Failed to load categories or products")
            st.stop()

        prod_tab = st.tabs(["View", "Add", "Update", "Delete"])

        # ----- View Products by Category -----
        with prod_tab[0]:
            st.subheader("📦 Products by Category")
            if not categories:
                st.warning("No categories found.")
            else:
                cat_map = {cat["name"]: cat["id"] for cat in categories}
                selected_cat = st.selectbox("Select Category", list(cat_map.keys()), key="view_category")
                selected_id = cat_map[selected_cat]
                filtered = [p for p in products if p["category_id"] == selected_id]

                if not filtered:
                    st.info("No products in this category.")
                else:
                    for p in filtered:
                        st.markdown(f"### {p['name']} - ₹{p['price']}")
                        st.write(p["description"])
                        st.write(f"Stock: {p['stock']}")
                        if p.get("image_url"):
                            st.image(p["image_url"], width=300)

        # ----- Admin: Add Product -----
        if user["is_admin"]:
            with prod_tab[1]:
                st.subheader("➕ Add Product")
                name = st.text_input("Product Name", key="add_name")
                desc = st.text_area("Description", key="add_desc")
                price = st.number_input("Price", min_value=0, key="add_price")
                stock = st.number_input("Stock", min_value=0, key="add_stock")
                cat_id = st.selectbox("Select Category", options=[c["id"] for c in categories], format_func=lambda x: next(c["name"] for c in categories if c["id"] == x), key="add_cat")
                img = st.text_input("Image URL", key="add_img")

                if st.button("Add Product", key="add_btn"):
                    res = create_product({
                        "name": name,
                        "description": desc,
                        "price": price,
                        "stock": stock,
                        "category_id": cat_id,
                        "image_url": img
                    })
                    if res.status_code == 200:
                        st.success("✅ Product added successfully!")

            # ----- Admin: Update Product -----
            with prod_tab[2]:
                st.subheader("✏️ Update Product")
                prod_map = {f"{p['name']} (ID:{p['id']})": p for p in products}
                sel = st.selectbox("Select Product to Update", list(prod_map.keys()), key="upd_select")
                p = prod_map[sel]

                name = st.text_input("Name", value=p["name"], key="upd_name")
                desc = st.text_area("Description", value=p["description"], key="upd_desc")
                price = st.number_input("Price", value=p["price"], key="upd_price")
                stock = st.number_input("Stock", value=p["stock"], key="upd_stock")
                cat_id = st.selectbox("Select Category", options=[c["id"] for c in categories], index=[c["id"] for c in categories].index(p["category_id"]), format_func=lambda x: next(c["name"] for c in categories if c["id"] == x), key="upd_cat")
                img = st.text_input("Image URL", value=p["image_url"], key="upd_img")

                if st.button("Update Product", key="upd_btn"):
                    res = update_product(p["id"], {
                        "name": name,
                        "description": desc,
                        "price": price,
                        "stock": stock,
                        "category_id": cat_id,
                        "image_url": img
                    })
                    if res.status_code == 200:
                        st.success("✅ Product updated!")

            # ----- Admin: Delete Product -----
            with prod_tab[3]:
                st.subheader("🗑️ Delete Product")
                del_sel = st.selectbox("Select Product to Delete", list(prod_map.keys()), key="del_select")
                prod_id = prod_map[del_sel]["id"]
                if st.button("Delete Product", key="del_btn"):
                    res = delete_product(prod_id)
                    if res.status_code == 200:
                        st.success("✅ Product deleted successfully!")

    
    
    

    elif menu == "Logout":
        st.session_state.access_token = None
        st.session_state.user_info = None
        st.success("✅ Logged out.")
        st.rerun()
