import streamlit as st
import pandas as pd
import json
import os
from fpdf import FPDF

# 1. PAGE CONFIG
st.set_page_config(page_title="EcoScan Kuwait", page_icon="🇰🇼", layout="wide")

USER_DB = "users_db.json"
ITEM_DB = "items_db.json"
FOUNDER_IMAGE = "founder.jpeg"
KUWAIT_AREAS = ["Asimah", "Hawalli", "Farwaniya", "Mubarak Al-Kabeer", "Ahmadi", "Jahra"]

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f: 
            try: return json.load(f)
            except: return []
    return []

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f)

# Initialize Session States
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "login"

# --- SIDEBAR: Founder & Account ---
with st.sidebar:
    st.title("🇰🇼 EcoScan Kuwait")
    
    # --- FOUNDER SECTION ---
    st.markdown("### 👤 Founder's Corner")
    if os.path.exists(FOUNDER_IMAGE):
        st.image(FOUNDER_IMAGE, use_container_width=True)
    else:
        st.warning("Photo not found. Please upload 'founder.jpg' to GitHub.")
    
    st.info("**Abilash's Vision:**\nWelcome! This platform is built to unite Kuwait in reducing waste. Join us today!")
    st.divider()

    # --- ACCOUNT SYSTEM ---
    if st.session_state.user is None:
        # LOGIN VIEW
        if st.session_state.view == "login":
            st.subheader("Login to Swap")
            l_phone = st.text_input("Phone Number", placeholder="e.g. 99887766")
            l_pass = st.text_input("Password", type="password")
            
            if st.button("Log In", type="primary", use_container_width=True):
                users = load_json(USER_DB)
                u = next((u for u in users if u['phone'] == l_phone and u['password'] == l_pass), None)
                if u:
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Invalid Login")
            
            st.write("---")
            if st.button("Don't have an account? Sign Up Here", use_container_width=True):
                st.session_state.view = "signup"
                st.rerun()

        # SIGN UP VIEW (The place to register)
        elif st.session_state.view == "signup":
            st.subheader("📝 New Member Registration")
            s_name = st.text_input("Full Name")
            s_phone = st.text_input("Mobile Number")
            s_area = st.selectbox("Your Governorate", KUWAIT_AREAS)
            s_pass = st.text_input("Create Password", type="password")
            
            if st.button("Register & Join", type="primary", use_container_width=True):
                if s_name and s_phone and s_pass:
                    users = load_json(USER_DB)
                    users.append({"name": s_name, "phone": s_phone, "area": s_area, "password": s_pass})
                    save_json(USER_DB, users)
                    st.success("Account Created! Please Login.")
                    st.session_state.view = "login"
                    st.rerun()
                else:
                    st.error("Please fill all fields")
            
            if st.button("Back to Login"):
                st.session_state.view = "login"
                st.rerun()
    else:
        st.success(f"Logged in as: {st.session_state.user['name']}")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

# --- MAIN PAGE CONTENT ---
st.title("🌱 EcoScan Kuwait")
if st.session_state.user:
    st.success(f"Welcome back to the portal, {st.session_state.user['name']}!")
    # Tabs for Map/Feed would go here
else:
    st.info("### Start Your Sustainability Journey")
    st.write("Please use the sidebar to **Sign Up** and join the community.")

