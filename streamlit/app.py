import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL")

st.set_page_config(page_title="🛒 E-Commerce App", layout="wide")

# -------------------- Session State Setup --------------------
defaults = {
    "access_token": None,
    "user_info": None,
    "cart": [],
    "menu_override": None,
    "order_success": False,
    "cat_name": "",
    "cat_desc": "",
    "cat_img": "",
    "prod_name": "",
    "prod_desc": "",
    "prod_price": 0,
    "prod_stock": 0,
    "prod_img": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------- API Helpers --------------------
def auth_header():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

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

def place_order(data):
    return requests.post(f"{API_URL}/orders/", json=data, headers=auth_header())

def fetch_my_orders():
    return requests.get(f"{API_URL}/orders/", headers=auth_header())

# -------------------- Auth Flow --------------------
if not st.session_state.access_token:
    auth_tab = st.sidebar.radio("Authentication", ["Login", "Register"])

    if auth_tab == "Login":
        st.title("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            res = login_user(email, password)
            if res.status_code == 200:
                st.session_state.access_token = res.json()["access_token"]
                st.session_state.user_info = get_profile().json()
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error(res.json().get("detail"))

    elif auth_tab == "Register":
        st.title("📝 Register")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        is_admin = st.checkbox("Register as Admin")
        if st.button("Register"):
            res = register_user(full_name, email, password, int(is_admin))
            if res.status_code == 200:
                st.success("✅ Registration successful. Please log in.")
            else:
                st.error(res.json().get("detail"))

else:
    user = st.session_state.user_info
    st.sidebar.markdown(f"👤 Welcome, **{user['full_name']}**")

    menu = st.sidebar.radio("Menu", ["Profile", "Categories", "Products", "Cart", "My Orders", "Logout"])

    if st.session_state.menu_override:
        menu = st.session_state.menu_override
        st.session_state.menu_override = None

    if menu == "Profile":
        st.title("👤 Profile")
        st.json(user)

    elif menu == "Categories":
        st.title("📂 Categories")
        cat_res = fetch_categories()
        categories = cat_res.json() if cat_res.status_code == 200 else []
        cat_tab = st.tabs(["View", "Add", "Update", "Delete"])

        with cat_tab[0]:
            st.subheader("📋 All Categories")
            for c in categories:
                st.markdown(f"### {c['name']}")
                st.write(c["description"])
                if c.get("image_url"):
                    st.image(c["image_url"], width=300)

        if user["is_admin"]:
            with cat_tab[1]:
                name = st.text_input("Category Name", value=st.session_state.cat_name, key="cat_name_input")
                desc = st.text_area("Description", value=st.session_state.cat_desc, key="cat_desc_input")
                img = st.text_input("Image URL", value=st.session_state.cat_img, key="cat_img_input")
                if st.button("Create Category"):
                    res = create_category({"name": name, "description": desc, "image_url": img})
                    if res.status_code == 200:
                        st.success("✅ Category created!")
                        st.session_state.cat_name = ""
                        st.session_state.cat_desc = ""
                        st.session_state.cat_img = ""
                        st.rerun()
                    else:
                        st.error(res.json().get("detail"))

            with cat_tab[2]:
                cat_map = {f"{c['name']} (ID:{c['id']})": c for c in categories}
                choice = st.selectbox("Select", list(cat_map.keys()), key="cat_update_select")
                cat = cat_map[choice]
                new_name = st.text_input("Name", value=cat["name"], key="cat_update_name")
                new_desc = st.text_area("Description", value=cat["description"], key="cat_update_desc")
                new_img = st.text_input("Image URL", value=cat["image_url"], key="cat_update_img")
                if st.button("Update"):
                    res = update_category(cat["id"], {"name": new_name, "description": new_desc, "image_url": new_img})
                    if res.status_code == 200:
                        st.success("✅ Updated successfully")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail"))

            with cat_tab[3]:
                del_choice = st.selectbox("Select", list(cat_map.keys()), key="cat_delete_select")
                del_id = cat_map[del_choice]["id"]
                if st.button("Delete Category"):
                    res = delete_category(del_id)
                    st.success("✅ Deleted" if res.status_code == 200 else res.json().get("detail"))
                    st.rerun()

    elif menu == "Products":
        st.title("🛍️ Products")
        cat_res, prod_res = fetch_categories(), fetch_products()
        categories = cat_res.json() if cat_res.status_code == 200 else []
        products = prod_res.json() if prod_res.status_code == 200 else []

        prod_tab = st.tabs(["View", "Add", "Update", "Delete"])

        with prod_tab[0]:
            st.subheader("📦 Products by Category")
            cat_map = {c["name"]: c["id"] for c in categories}
            selected_cat = st.selectbox("Select Category", list(cat_map.keys()), key="view_product_cat_select")
            selected_id = cat_map[selected_cat]
            filtered = [p for p in products if p["category_id"] == selected_id]

            for i, p in enumerate(filtered):
                st.markdown(f"### {p['name']} - ₹{p['price']}")
                st.write(p["description"])
                st.write(f"Stock: {p['stock']}")
                if p.get("image_url"):
                    st.image(p["image_url"], width=250)
                qty = st.number_input(f"Qty for {p['name']}", min_value=1, max_value=p["stock"], value=1, key=f"qty_{i}")
                if st.button(f"🛒 Add {p['name']} to Cart", key=f"add_{i}"):
                    st.session_state.cart.append({
                        "product_id": p["id"],
                        "name": p["name"],
                        "price": p["price"],
                        "quantity": qty
                    })
                    st.success(f"{p['name']} added to cart!")

        if user["is_admin"]:
            with prod_tab[1]:
                name = st.text_input("Product Name", value=st.session_state.prod_name, key="prod_name_input")
                desc = st.text_area("Description", value=st.session_state.prod_desc, key="prod_desc_input")
                price = st.number_input("Price", min_value=0, value=st.session_state.prod_price, key="prod_price_input")
                stock = st.number_input("Stock", min_value=0, value=st.session_state.prod_stock, key="prod_stock_input")
                cat_id = st.selectbox("Select Category", [c["id"] for c in categories],
                                      format_func=lambda x: next(c["name"] for c in categories if c["id"] == x),
                                      key="add_product_cat_select")
                img = st.text_input("Image URL", value=st.session_state.prod_img, key="prod_img_input")
                if st.button("Add Product"):
                    res = create_product({
                        "name": name, "description": desc, "price": price,
                        "stock": stock, "category_id": cat_id, "image_url": img
                    })
                    if res.status_code == 200:
                        st.success("✅ Product added!")
                        st.session_state.prod_name = ""
                        st.session_state.prod_desc = ""
                        st.session_state.prod_price = 0
                        st.session_state.prod_stock = 0
                        st.session_state.prod_img = ""
                        st.rerun()
                    else:
                        st.error(res.json().get("detail"))

            with prod_tab[2]:
                prod_map = {f"{p['name']} (ID:{p['id']})": p for p in products}
                sel = st.selectbox("Select Product", list(prod_map.keys()), key="update_product_select")
                p = prod_map[sel]
                name = st.text_input("Name", value=p["name"], key="update_name")
                desc = st.text_area("Description", value=p["description"], key="update_desc")
                price = st.number_input("Price", value=p["price"], key="update_price")
                stock = st.number_input("Stock", value=p["stock"], key="update_stock")
                cat_id = st.selectbox("Category", [c["id"] for c in categories],
                                      index=[c["id"] for c in categories].index(p["category_id"]),
                                      format_func=lambda x: next(c["name"] for c in categories if c["id"] == x),
                                      key="update_product_cat_select")
                img = st.text_input("Image URL", value=p["image_url"], key="update_img")
                if st.button("Update Product"):
                    res = update_product(p["id"], {
                        "name": name, "description": desc, "price": price,
                        "stock": stock, "category_id": cat_id, "image_url": img
                    })
                    if res.status_code == 200:
                        st.success("✅ Product updated!")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail"))

            with prod_tab[3]:
                del_sel = st.selectbox("Select Product", list(prod_map.keys()), key="delete_product_select")
                prod_id = prod_map[del_sel]["id"]
                if st.button("Delete Product"):
                    res = delete_product(prod_id)
                    st.success("✅ Deleted" if res.status_code == 200 else res.json().get("detail"))
                    st.rerun()

    elif menu == "Cart":
        st.title("🛒 Your Cart")
        cart = st.session_state.cart

        if st.session_state.order_success:
            st.success("🎉 Order placed successfully!")
            if st.button("🛍️ Continue Shopping"):
                st.session_state.order_success = False
                st.session_state.menu_override = "Products"
                st.rerun()

        if not cart:
            st.info("Your cart is empty.")
        else:
            total = 0
            for i, item in enumerate(cart):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                with col1:
                    st.write(f"**{item['name']}**")
                with col2:
                    qty = st.number_input("Qty", min_value=1, value=item['quantity'], key=f"qty_cart_{i}")
                    item['quantity'] = qty
                with col3:
                    st.write(f"₹ {item['price']} × {item['quantity']} = ₹{item['price'] * item['quantity']}")
                with col4:
                    if st.button("❌ Remove", key=f"remove_{i}"):
                        st.session_state.cart.pop(i)
                        st.rerun()
                total += item['price'] * item['quantity']

            st.markdown(f"### 🧾 Total: ₹ {total}")
            if st.button("✅ Place Order"):
                order_payload = {
                    "items": [{"product_id": item["product_id"], "quantity": item["quantity"]} for item in cart]
                }
                res = place_order(order_payload)
                if res.status_code in (200, 201):
                    st.session_state.cart = []
                    st.session_state.order_success = True
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Failed to place order."))

    elif menu == "My Orders":
        st.title("📦 My Orders")
        res = fetch_my_orders()
        if res.status_code == 200:
            orders = res.json()
            if not orders:
                st.info("No orders placed yet.")
            else:
                for order in orders:
                    with st.expander(f"Order #{order['id']} - ₹{order['total_amount']} - {order['status']}"):
                        for item in order['items']:
                            product_name = item.get("product_name", f"Product ID {item['product_id']}")
                            st.markdown(f"- **{product_name}** × {item['quantity']} @ ₹{item['price']} each")
        else:
            st.error("❌ Failed to fetch orders.")

    elif menu == "Logout":
        for key in defaults:
            st.session_state[key] = defaults[key]
        st.success("✅ Logged out.")
        st.rerun()

        