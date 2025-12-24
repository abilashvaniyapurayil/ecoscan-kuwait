import streamlit as st
import pandas as pd
import json
import os
from fpdf import FPDF

# 1. GLOBAL BRANDING & PAGE CONFIG
st.set_page_config(
    page_title="EcoScan Kuwait", 
    page_icon="🇰🇼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Database & Constants ---
USER_DB = "users_db.json"
ITEM_DB = "items_db.json"
KUWAIT_AREAS = ["Asimah", "Hawalli", "Farwaniya", "Mubarak Al-Kabeer", "Ahmadi", "Jahra"]

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f: 
            try:
                return json.load(f)
            except:
                return []
    return []

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f)

# --- Session State Management ---
if "user" not in st.session_state:
    st.session_state.user = None
if "view" not in st.session_state:
    st.session_state.view = "login"

# --- Sidebar: Account & Profile Management ---
st.sidebar.title("🇰🇼 EcoScan Account")

if st.session_state.user is None:
    # Social Login UI (Reminders for Meta/Google integration)
    st.sidebar.markdown("### Quick Access")
    st.sidebar.button("Continue with Google 🌐", use_container_width=True)
    st.sidebar.button("Continue with Facebook 🔵", use_container_width=True)
    st.sidebar.divider()

    if st.session_state.view == "login":
        st.sidebar.subheader("Login")
        l_phone = st.sidebar.text_input("Mobile Number")
        l_pass = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Log In", type="primary", use_container_width=True):
            users = load_json(USER_DB)
            u = next((u for u in users if u['phone'] == l_phone and u['password'] == l_pass), None)
            if u:
                st.session_state.user = u
                st.sidebar.success(f"Welcome back, {u['name']}!")
                st.rerun()
            else: st.sidebar.error("Account not found or wrong password")
        
        col1, col2 = st.sidebar.columns(2)
        if col1.button("Create Account"): st.session_state.view = "signup"; st.rerun()
        if col2.button("Forgot Pass?"): st.session_state.view = "forgot"; st.rerun()

    elif st.session_state.view == "signup":
        st.sidebar.subheader("New Member Registration")
        s_name = st.sidebar.text_input("Full Name")
        s_phone = st.sidebar.text_input("Mobile Number")
        s_area = st.sidebar.selectbox("Governorate", KUWAIT_AREAS)
        s_pass = st.sidebar.text_input("Create Password", type="password")
        if st.sidebar.button("Register Now", use_container_width=True):
            users = load_json(USER_DB)
            if any(u['phone'] == s_phone for u in users):
                st.sidebar.error("Number already exists!")
            else:
                users.append({"name": s_name, "phone": s_phone, "area": s_area, "password": s_pass, "points": 0})
                save_json(USER_DB, users)
                st.sidebar.success("Account created! Please Login.")
                st.session_state.view = "login"; st.rerun()
        if st.sidebar.button("Back to Login"): st.session_state.view = "login"; st.rerun()

    elif st.session_state.view == "forgot":
        st.sidebar.subheader("Password Recovery")
        f_phone = st.sidebar.text_input("Registered Mobile")
        f_new = st.sidebar.text_input("Enter New Password", type="password")
        if st.sidebar.button("Reset Password", use_container_width=True):
            users = load_json(USER_DB)
            found = False
            for u in users:
                if u['phone'] == f_phone:
                    u['password'] = f_new
                    found = True; break
            if found:
                save_json(USER_DB, users)
                st.sidebar.success("Updated! Please login.")
                st.session_state.view = "login"; st.rerun()
            else: st.sidebar.error("Mobile number not found.")
        if st.sidebar.button("Back"): st.session_state.view = "login"; st.rerun()

else:
    # LOGGED IN: Profile & Edit Mode
    st.sidebar.success(f"Verified Member: {st.session_state.user['name']}")
    
    with st.sidebar.expander("⚙️ Edit My Profile"):
        e_name = st.text_input("Name", value=st.session_state
