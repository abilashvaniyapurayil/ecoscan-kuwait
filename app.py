import streamlit as st
import pandas as pd
import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components

# --- 1. SEARCH & SOCIAL VERIFICATION ---
# YOUR GOOGLE TAG INTEGRATED BELOW
GOOGLE_TAG = "UbGI9p25Kivjr9u465NRYSpRTy4euChN-XFrwiy3r40"
META_TAG = "YOUR_META_VERIFICATION_CODE_HERE" 

# This component injects the verification into the app's HTML
components.html(
    f"""
    <html>
        <head>
            <meta name="google-site-verification" content="{GOOGLE_TAG}" />
            <meta name="facebook-domain-verification" content="{META_TAG}" />
        </head>
    </html>
    """,
    height=0,
)

# --- 2. MOBILE APP CONFIG ---
st.set_page_config(
    page_title="EcoScan Kuwait",
    page_icon="🇰🇼",
    layout="centered"
)

# --- 3. PROFESSIONAL MOBILE STYLING (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #F1F8E9; }
    .main-banner {
        background-color: #2E7D32;
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .stButton>button {
        border-radius: 25px;
        width: 100%;
        height: 3.5em;
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
    }
    div.stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA ENGINE (JSON) ---
USER_DB = "users_db.json"
ITEM_DB = "items_db.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# --- 5. SESSION LOGIC ---
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "login"

# --- 6. MAIN APP INTERFACE ---
if st.session_state.user:
    is_admin = st.session_state.user.get("role") == "admin"
    st.markdown('<div class="main-banner"><h1>EcoScan Kuwait</h1><p>Sustainability and Community Swaps</p></div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📤 Post", "📱 Feed", "🏆 Top", "⚖️ Legal"])

    with tabs[0]:
        st.subheader("Add a New Listing")
        with st.form("post_item", clear_on_submit=True):
            name = st.text_input("Item Name")
            cat = st.selectbox("Category", ["Electronics", "Furniture", "Books", "Clothes", "Other"])
            if st.form_submit_button("Post & Earn 10 Points"):
                if name:
                    items = load_data(ITEM_DB)
                    items.append({"id": str(datetime.now().timestamp()), "name": name, "cat": cat, "user": st.session_state.user['name'], "area": st.session_state.user['area']})
                    save_data(ITEM_DB, items)
                    
                    users = load_data(USER_DB)
                    for u in users:
                        if u['phone'] == st.session_state.user['phone']:
                            u['points'] = u.get('points', 0) + 10
                            break
                    save_data(USER_DB, users)
                    st.success("Item Live! +10 Points Earned.")
                    st.rerun()

    with tabs[1]:
        st.subheader("Live Feed")
        items = load_data(ITEM_DB)
        for i in reversed(items):
            with st.container(border=True):
                st.write(f"### {i['name']}")
                st.caption(f"📍 {i['area']} | Category: {i['cat']}")
                if is_admin:
                    if st.button("Delete Listing", key=f"del_{i['id']}"):
                        items = [item for item in items if item['id'] != i['id']]
                        save_data(ITEM_DB, items)
                        st.rerun()

    with tabs[2]:
        st.subheader("🏆 Leaderboard")
        all_users = load_data(USER_DB)
        if all_users:
            df = pd.DataFrame(all_users)[['name', 'area', 'points']].sort_values('points', ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[3]:
        st.subheader("⚖️ Privacy Policy")
        st.info("Verified Property for Google and App Store compliance.")
        st.write("1. Data used only for local swap verification.")
        st.write("2. Contact support for account deletion.")
        st.link_button("Founder Support (WhatsApp)", "https://wa.me/96512345678")

else:
    # --- LOGIN / SIGNUP ---
    st.title("🇰🇼 EcoScan Kuwait")
    if st.session_state.view == "login":
        phone = st.text_input("Mobile Number")
        pw = st.text_input("Password", type="password")
        if st.button("Log In"):
            if phone == "admin" and pw == "admin123":
                st.session_state.user = {"name": "Founder", "phone": "admin", "area": "Kuwait City", "role": "admin"}
                st.rerun()
            users = load_data(USER_DB)
            u = next((u for u in users if u['phone'] == phone and u['password'] == pw), None)
            if u: st.session_state.user = u; st.rerun()
            else: st.error("Verification Error")
        if st.button("New User? Register"): st.session_state.view = "signup"; st.rerun()
    else:
        n = st.text_input("Full Name")
        p = st.text_input("Mobile Number")
        a = st.selectbox("Governorate", ["Asimah", "Hawalli", "Farwaniya", "Ahmadi", "Jahra", "Mubarak"])
        pw_n = st.text_input("Create Password", type="password")
        if st.button("Join Now"):
            users = load_data(USER_DB)
            users.append({"name": n, "phone": p, "area": a, "password": pw_n, "points": 10})
            save_data(USER_DB, users)
            st.success("Account Created!")
            st.session_state.view = "login"
            st.rerun()
