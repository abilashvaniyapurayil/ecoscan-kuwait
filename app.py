import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(page_title="EcoScan Kuwait", page_icon="🇰🇼", layout="wide")

# --- Database Setup ---
USER_DB = "users_db.json"
ITEM_DB = "items_db.json"
FOUNDER_IMAGE = "founder.jpeg" 
KUWAIT_AREAS = ["Asimah", "Hawalli", "Farwaniya", "Mubarak Al-Kabeer", "Ahmadi", "Jahra"]
CATEGORIES = ["Furniture", "Electronics", "Books", "Clothes", "Appliances", "Other"]

# --- Sustainability Tips List ---
TIPS = [
    "💧 **Tip:** Fix leaking taps! A single drip can waste over 50 liters of water a day in Kuwait.",
    "🛍️ **Tip:** Bring your own reusable bags when shopping at Co-ops to reduce plastic waste.",
    "💡 **Tip:** Switch to LED bulbs. They last 25 times longer and use 75% less energy.",
    "♻️ **Tip:** Before throwing something away, ask: 'Can I swap this on EcoScan first?'",
    "☀️ **Tip:** Close your curtains during peak sunlight hours to keep your home cool and save AC energy."
]

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
    st.header("🇰🇼 EcoScan Kuwait")
    
    # Founder's Corner
    st.subheader("👤 Founder's Corner")
    if os.path.exists(FOUNDER_IMAGE):
        st.image(FOUNDER_IMAGE, use_container_width=True)
        st.info("**Abilash's Message:** Welcome back! Check out today's green tip and see where you rank on the leaderboard.")
        st.link_button("💬 Chat with Founder", "https://wa.me/96512345678", use_container_width=True)
    
    st.divider()

    # Account Management
    if st.session_state.user is None:
        if st.session_state.view == "login":
            st.markdown("### 🔑 Login")
            l_phone = st.text_input("Phone Number")
            l_pass = st.text_input("Password", type="password")
            if st.button("Log In", type="primary", use_container_width=True):
                users = load_json(USER_DB)
                u = next((u for u in users if u['phone'] == l_phone and u['password'] == l_pass), None)
                if u:
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Invalid credentials")
            if st.button("New User? Sign Up"): st.session_state.view = "signup"; st.rerun()

        elif st.session_state.view == "signup":
            st.markdown("### 📝 Register")
            s_name = st.text_input("Full Name")
            s_phone = st.text_input("Mobile Number")
            s_area = st.selectbox("Governorate", KUWAIT_AREAS)
