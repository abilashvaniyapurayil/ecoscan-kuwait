import streamlit as st
import pandas as pd
import json
import os
from fpdf import FPDF

# 1. PAGE CONFIG
st.set_page_config(page_title="EcoScan Kuwait", page_icon="🇰🇼", layout="wide")

# --- Database Setup ---
USER_DB = "users_db.json"
ITEM_DB = "items_db.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f: return json.load(f)
    return []

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f)

# --- Authentication Logic ---
if "user" not in st.session_state:
    st.session_state.user = None

def sign_up(name, phone, area, password):
    users = load_json(USER_DB)
    if any(u['phone'] == phone for u in users):
        return False
    users.append({"name": name, "phone": phone, "area": area, "password": password, "points": 0})
    save_json(USER_DB, users)
    return True

def login(phone, password):
    users = load_json(USER_DB)
    for u in users:
        if u['phone'] == phone and u['password'] == password:
            return u
    return None

# --- UI: Login / Profile Sidebar ---
st.sidebar.title("👤 My Profile")
if st.session_state.user is None:
    tab_auth = st.sidebar.tabs(["Login", "Sign Up"])
    with tab_auth[0]:
        l_phone = st.text_input("Phone Number")
        l_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            u = login(l_phone, l_pass)
            if u: 
                st.session_state.user = u
                st.rerun()
            else: st.error("Wrong credentials")
    with tab_auth[1]:
        s_name = st.text_input("Full Name")
        s_phone = st.text_input("Mobile No.")
        s_area = st.selectbox("Area", ["Asimah", "Hawalli", "Farwaniya", "Ahmadi", "Jahra"])
        s_pass = st.text_input("New Password", type="password")
        if st.button("Register"):
            if sign_up(s_name, s_phone, s_area, s_pass):
                st.success("Account created! Please login.")
            else: st.error("Number already registered")
else:
    st.sidebar.write(f"Welcome, **{st.session_state.user['name']}**!")
    st.sidebar.write(f"📍 Location: {st.session_state.user['area']}")
    st.sidebar.write(f"📞 Contact: {st.session_state.user['phone']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

# --- Main App Logic ---
st.title("🇰🇼 EcoScan: Kuwait Member Portal")

if st.session_state.user is None:
    st.info("Please Login or Sign Up from the sidebar to start swapping items!")
else:
    t1, t2, t3 = st.tabs(["📤 Post Item", "📍 Map", "🏆 Leaderboard"])

    with t1:
        st.subheader("Post a New Item")
        i_name = st.text_input("Item Name")
        i_cat = st.selectbox("Category", ["Furniture", "Electronics", "Clothes"])
        if st.button("Post Item"):
            items = load_json(ITEM_DB)
            # Link item to the logged-in user
            new_item = {
                "name": i_name,
                "user": st.session_state.user['name'],
                "phone": st.session_state.user['phone'],
                "area": st.session_state.user['area'],
                "cat": i_cat,
                "lat": 29.37, "lon": 47.97 # Simplified location
            }
            items.append(new_item)
            save_json(ITEM_DB, items)
            st.success("Item posted! Neighbors can now see your contact info.")
            st.balloons()

    with t2:
        st.subheader("Kuwait Eco-Map")
        items = load_json(ITEM_DB)
        if items:
            df = pd.DataFrame(items)
            st.map(df)
        
    with t3:
        st.subheader("Community Rankings")
        users = load_json(USER_DB)
        if users:
            st.table(pd.DataFrame(users)[['name', 'area', 'phone']])
