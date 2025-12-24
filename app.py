import streamlit as st
import pandas as pd
import json
import os
import random
import base64
from datetime import datetime

# --- 1. CONFIG ---
st.set_page_config(page_title="EcoScan Kuwait | Admin", page_icon="🇰🇼", layout="wide")

USER_DB = "users_db.json"
ITEM_DB = "items_db.json"
FEEDBACK_DB = "feedback_db.json"
FOUNDER_IMAGE = "founder.jpeg"

# --- 2. DATA UTILS ---
def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def image_to_base64(uploaded_file):
    if uploaded_file: return base64.b64encode(uploaded_file.getvalue()).decode()
    return None

# --- 3. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "login"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🇰🇼 EcoScan")
    if os.path.exists(FOUNDER_IMAGE):
        st.image(FOUNDER_IMAGE, caption="Founder: Abilash Vani")
    
    if st.session_state.user:
        st.success(f"Logged in as: {st.session_state.user['name']}")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        # Professional Login
        st.subheader("Login")
        u_phone = st.text_input("Phone (Use 'admin' for Dashboard)")
        u_pw = st.text_input("Password", type="password")
        if st.button("Login", type="primary", use_container_width=True):
            # Admin Trapdoor
            if u_phone == "admin" and u_pw == "admin123":
                st.session_state.user = {"name": "Founder Admin", "phone": "admin", "area": "Kuwait City", "role": "admin"}
                st.rerun()
            else:
                users = load_data(USER_DB)
                u = next((u for u in users if u['phone'] == u_phone and u['password'] == u_pw), None)
                if u:
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Invalid Login")
        if st.button("New User? Sign Up"): st.session_state.view = "signup"; st.rerun()

# --- 5. MAIN INTERFACE ---
if st.session_state.user:
    # Admin check
    is_admin = st.session_state.user.get("role") == "admin"
    
    tabs = ["📤 Post", "📱 Feed", "🏆 Rankings"]
    if is_admin: tabs.append("🔧 Founder Control")
    
    active_tabs = st.tabs(tabs)

    # TAB: POST
    with active_tabs[0]:
        st.subheader("List a New Item")
        with st.form("post_item"):
            name = st.text_input("Item Name")
            cat = st.selectbox("Category", ["Electronics", "Furniture", "Books", "Other"])
            img = st.file_uploader("Photo", type=['jpg','png'])
            if st.form_submit_button("Publish"):
                items = load_data(ITEM_DB)
                items.append({
                    "id": str(datetime.now().timestamp()),
                    "name": name, "user": st.session_state.user['name'],
                    "area": st.session_state.user['area'], "cat": cat,
                    "image": image_to_base64(img)
                })
                save_data(ITEM_DB, items)
                st.success("Item Published!")

    # TAB: FEED
    with active_tabs[1]:
        items = load_data(ITEM_DB)
        for i in reversed(items):
            with st.container(border=True):
                c1, c2 = st.columns([1, 3])
                if i.get("image"): c1.image(base64.b64decode(i["image"]))
                c2.markdown(f"### {i['name']} ({i['cat']})")
                c2.caption(f"📍 {i['area']} | Owner: {i['user']}")
                if is_admin:
                    if c2.button(f"Delete Listing", key=f"del_{i['id']}"):
                        items = [item for item in items if item['id'] != i['id']]
                        save_data(ITEM_DB, items)
                        st.rerun()

    # TAB: RANKINGS
    with active_tabs[2]:
        all_users = load_data(USER_DB)
        if all_users:
            st.table(pd.DataFrame(all_users)[['name', 'points']].sort_values('points', ascending=False))

    # TAB: ADMIN CONTROL (Only visible to you!)
    if is_admin:
        with active_tabs[3]:
            st.header("🛡️ Founder Control Panel")
            col1, col2 = st.columns(2)
            
            all_users = load_data(USER_DB)
            all_items = load_data(ITEM_DB)
            
            col1.metric("Total Users", len(all_users))
            col2.metric("Total Swaps", len(all_items))
            
            st.subheader("Manage Users")
            user_df = pd.DataFrame(all_users)
            st.dataframe(user_df)
            
            st.subheader("User Feedback")
            feedback = load_data(FEEDBACK_DB)
            if feedback: st.write(feedback)
            else: st.info("No feedback yet.")

else:
    st.title("EcoScan Kuwait")
    st.info("Please login via the sidebar to start swapping.")
