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
FEEDBACK_DB = "feedback_db.json" # New database for your suggestions
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
        st.info("**Abilash's Message:** Thank you for joining! Your feedback helps me improve this app for all of Kuwait.")
        st.link_button("💬 WhatsApp Me", "https://wa.me/96512345678", use_container_width=True)
    
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
            s_pass = st.text_input("Password", type="password")
            if st.button("Join & Get 10 Points!", type="primary", use_container_width=True):
                users = load_json(USER_DB)
                users.append({"name": s_name, "phone": s_phone, "area": s_area, "password": s_pass, "points": 10})
                save_json(USER_DB, users)
                st.success("Account Created! Please Login.")
                st.session_state.view = "login"; st.rerun()
            if st.button("Back"): st.session_state.view = "login"; st.rerun()
    else:
        st.success(f"Verified: {st.session_state.user['name']}")
        users = load_json(USER_DB)
        db_user = next((u for u in users if u['phone'] == st.session_state.user['phone']), st.session_state.user)
        st.metric(label="🌱 My Eco-Points", value=f"{db_user.get('points', 0)} PTS")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None; st.rerun()

# --- MAIN PAGE CONTENT ---
st.title("🌱 EcoScan Kuwait")

if st.session_state.user:
    # Tip of the Day
    st.chat_message("assistant").write(random.choice(TIPS))
    
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Post & Earn", "📱 Search Feed", "🏆 Leaderboard", "📩 Contact Founder"])

    # TAB 1: POSTING
    with tab1:
        st.subheader("Add an Item")
        c1, c2 = st.columns(2)
        with c1:
            item_name = st.text_input("Item Name")
            item_desc = st.text_area("Description")
        with c2:
            item_cat = st.selectbox("Category", CATEGORIES)
            item_cond = st.select_slider("Condition", options=["Fair", "Good", "Excellent", "New"])

        if st.button("🚀 Publish Item", type="primary"):
            if item_name:
                items = load_json(ITEM_DB)
                items.append({
                    "id": str(datetime.now().timestamp()),
                    "name": item_name, "desc": item_desc, "cat": item_cat, "cond": item_cond,
                    "user": st.session_state.user['name'], "area": st.session_state.user['area'],
                    "date": datetime.now().strftime("%d %b %Y")
                })
                save_json(ITEM_DB, items)
                
                # Update Points
                users = load_json(USER_DB)
                for u in users:
                    if u['phone'] == st.session_state.user['phone']:
                        u['points'] = u.get('points', 0) + 10
                        break
                save_json(USER_DB, users)
                st.success("
