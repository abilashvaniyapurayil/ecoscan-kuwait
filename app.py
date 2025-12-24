import streamlit as st
import pandas as pd
import json
import os
import random
import base64
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. MOBILE-FIRST APP CONFIG ---
st.set_page_config(
    page_title="EcoScan Kuwait",
    page_icon="🇰🇼",
    layout="centered", # Better for mobile "wrapper" apps
    initial_sidebar_state="collapsed"
)

# --- 2. THEME & MOBILE UI CUSTOMIZATION ---
st.markdown("""
    <style>
    /* Professional Banner */
    .stApp { background-color: #F1F8E9; }
    .main-banner {
        background-color: #2E7D32;
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    /* Mobile Navigation Style */
    div.stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE & EMAIL SETTINGS ---
USER_DB = "users_db.json"
ITEM_DB = "items_db.json"
FEEDBACK_DB = "feedback_db.json"
FOUNDER_IMAGE = "founder.jpeg"
# UPDATE THESE FOR EMAILS TO WORK
SENDER_EMAIL = "your-email@gmail.com" 
SENDER_PASSWORD = "your-app-password" 

def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def send_welcome_email(user_email, user_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"EcoScan Kuwait <{SENDER_EMAIL}>"
        msg['To'] = user_email
        msg['Subject'] = "Welcome to the Green Movement! 🌱"
        body = f"<h2>Marhaba {user_name}!</h2><p>You are now an Eco-Warrior. Start swapping to earn points!</p>"
        msg.attach(MIMEText(body, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except: pass # Fails silently if credentials aren't set yet

# --- 4. SESSION MANAGEMENT ---
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "login"

# --- 5. SIDEBAR (FOUNDER'S CORNER) ---
with st.sidebar:
    st.title("🇰🇼 EcoScan")
    if os.path.exists(FOUNDER_IMAGE):
        st.image(FOUNDER_IMAGE, caption="Abilash Vani, Founder") #
    
    if st.session_state.user:
        st.success(f"User: {st.session_state.user['name']}")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

# --- 6. MAIN PORTAL LOGIC ---
if st.session_state.user:
    # Admin Trapdoor
    is_admin = st.session_state.user.get("role") == "admin"
    
    st.markdown('<div class="main-banner"><h1>EcoScan Kuwait</h1><p>Kuwait\'s National Swap Network</p></div>', unsafe_allow_html=True)
    
    # Navigation Tabs
    tabs = ["📤 Post", "📱 Feed", "🏆 Top", "⚖️ Legal"]
    if is_admin: tabs.append("🔧 Admin")
    
    active_tabs = st.tabs(tabs)

    # TAB 1: POST ITEM
    with active_tabs[0]:
        st.subheader("Earn 10 Eco-Points")
        with st.form("post_form"):
            name = st.text_input("Item Name")
            cat = st.selectbox("Category", ["Electronics", "Furniture", "Books", "Other"])
            img = st.file_uploader("Photo", type=['jpg','png'])
            if st.form_submit_button("Publish Nationally"):
                if name:
                    items = load_data(ITEM_DB)
                    items.append({
                        "id": str(datetime.now().timestamp()),
                        "name": name, "user": st.session_state.user['name'],
                        "area": st.session_state.user['area'], "cat": cat,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    save_data(ITEM_DB, items)
                    # Point Reward Logic
                    users = load_data(USER_DB)
                    for u in users:
                        if u['phone'] == st.session_state.user['phone']: u['points'] = u.get('points', 0) + 10
                    save_data(USER_DB, users)
                    st.success("Success! +10 Points.")
                    st.rerun()

    # TAB 2: LIVE FEED
    with active_tabs[1]:
        st.subheader("Community Swaps")
        search = st.text_input("🔍 Search area or item...")
        items = load_data(ITEM_DB)
        filtered = [i for i in items if search.lower() in i['name'].lower() or search.lower() in i['area'].lower()]
        for i in reversed(filtered):
            with st.container(border=True):
                st.write(f"### {i['name']}")
                st.caption(f"📍 {i['area']} | 👤 {i['user']}")
                if is_admin:
                    if st.button("Delete Listing", key=f"del_{i['id']}"):
                        items = [item for item in items if item['id'] != i['id']]
                        save_data(ITEM_DB, items)
                        st.rerun()

    # TAB 3: LEADERBOARD
    with active_tabs[2]:
        st.subheader("🏆 National Rankings")
        all_users = load_data(USER_DB)
        if all_users:
            df = pd.DataFrame(all_users)[['name', 'area', 'points']].sort_values('points', ascending=False)
            st.table(df.head(10))

    # TAB 4: LEGAL (App Store Required)
    with active_tabs[3]:
        st.subheader("Privacy & Terms")
        st.write("EcoScan Kuwait respects your data. We collect phone numbers for verification only. You can delete your account via the support button.")
        st.link_button("Contact Support", "https://wa.me/96512345678")

    # TAB 5: ADMIN PANEL
    if is_admin:
        with active_tabs[4]:
            st.header("Founder Control")
            st.metric("Total Users", len(load_data(USER_DB)))
            st.dataframe(pd.DataFrame(load_data(USER_DB)))

else:
    # --- LOGIN / SIGNUP VIEW ---
    st.title("🌱 EcoScan Kuwait")
    
    if st.session_state.view == "login":
        phone = st.text_input("Mobile Number")
        pw = st.text_input("Password", type="password")
        if st.button("Log In", type="primary", use_container_width=True):
            if phone == "admin" and pw == "admin123":
                st.session_state.user = {"name": "Admin", "phone": "admin", "area": "Kuwait", "role": "admin"}
                st.rerun()
            users = load_data(USER_DB)
            u = next((u for u in users if u['phone'] == phone and u['password'] == pw), None)
            if u: st.session_state.user = u; st.rerun()
            else: st.error("Wrong details")
        if st.button("New? Register Here"): st.session_state.view = "signup"; st.rerun()
    
    else:
        s_name = st.text_input("Full Name")
        s_email = st.text_input("Email Address")
        s_phone = st.text_input("Mobile")
        s_area = st.selectbox("Governorate", ["Asimah", "Hawalli", "Farwaniya", "Ahmadi", "Jahra", "Mubarak"])
        s_pw = st.text_input("Password", type="password")
        if st.button("Register & Get 10 Pts", type="primary", use_container_width=True):
            users = load_data(USER_DB)
            users.append({"name": s_name, "email": s_email, "phone": s_phone, "area": s_area, "password": s_pw, "points": 10})
            save_data(USER_DB, users)
            send_welcome_email(s_email, s_name)
            st.success("Welcome! You can now log in.")
            st.session_state.view = "login"
            st.rerun()
        if st.button("Back to Login"): st.session_state.view = "login"; st.rerun()
