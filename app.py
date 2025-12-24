import streamlit as st
import pandas as pd
import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. GOOGLE SEARCH CONSOLE VERIFICATION LOGIC ---
# This section handles the HTML file verification Google requested.
query_params = st.query_params
if "verify" in query_params and query_params["verify"] == "google":
    st.write("google-site-verification: google301238ef8c60a6de.html")
    st.stop() 

# --- 2. MOBILE APP CONFIGURATION ---
st.set_page_config(
    page_title="EcoScan Kuwait",
    page_icon="🇰🇼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 3. PROFESSIONAL MOBILE UI (CSS) ---
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
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    .stButton>button {
        border-radius: 25px;
        width: 100%;
        height: 3.5em;
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
        border: none;
    }
    div.stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA MANAGEMENT ENGINE ---
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

# --- 5. SESSION STATE ---
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "login"

# --- 6. MAIN INTERFACE ---
if st.session_state.user:
    is_admin = st.session_state.user.get("role") == "admin"
    
    st.markdown('<div class="main-banner"><h1>EcoScan Kuwait</h1><p>National Sustainability & Swap Portal</p></div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📤 Post", "📱 Feed", "🏆 Top", "⚖️ Legal"])

    # --- TAB: POST ITEM ---
    with tabs[0]:
        st.subheader("List a New Item")
        with st.form("post_item", clear_on_submit=True):
            name = st.text_input("What are you swapping?")
            cat = st.selectbox("Category", ["Electronics", "Furniture", "Books", "Other"])
            desc = st.text_area("Details (Condition, Pickup location)")
            if st.form_submit_button("Publish (+10 Eco-Points)"):
                if name:
                    items = load_data(ITEM_DB)
                    items.append({
                        "id": str(datetime.now().timestamp()),
                        "name": name, "cat": cat, "desc": desc,
                        "user": st.session_state.user['name'],
                        "area": st.session_state.user['area']
                    })
                    save_data(ITEM_DB, items)
                    # Reward Points
                    users = load_data(USER_DB)
                    for u in users:
                        if u['phone'] == st.session_state.user['phone']:
                            u['points'] = u.get('points', 0) + 10
                    save_data(USER_DB, users)
                    st.success("Item Live! Points added to your profile.")
                    st.rerun()

    # --- TAB: LIVE FEED ---
    with tabs[1]:
        st.subheader("Community Marketplace")
        search = st.text_input("🔍 Search area or item...")
        items = load_data(ITEM_DB)
        filtered = [i for i in items if search.lower() in i['area'].lower() or search.lower() in i['name'].lower()]
        
        for i in reversed(filtered):
            with st.container(border=True):
                st.write(f"### {i['name']}")
                st.caption(f"📍 {i['area']} | Owner: {i['user']}")
                st.write(i.get('desc', 'No description provided.'))
                if is_admin:
                    if st.button("Delete Listing", key=f"del_{i['id']}"):
                        items = [item for item in items if item['id'] != i['id']]
                        save_data(ITEM_DB, items)
                        st.rerun()

    # --- TAB: LEADERBOARD ---
    with tabs[2]:
        st.subheader("🏆 Kuwait's Top Eco-Warriors")
        all_users = load_data(USER_DB)
        if all_users:
            df = pd.DataFrame(all_users)[['name', 'area', 'points']].sort_values('points', ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB: LEGAL & PRIVACY ---
    with tabs[3]:
        st.subheader("⚖️ Privacy Policy")
        st.info("Verified Property: google301238ef8c60a6de.html")
        st.write("EcoScan Kuwait is committed to data privacy. We use your mobile number only for account verification and security.")
        st.link_button("Founder Support (WhatsApp)", "https://wa.me/96512345678")

else:
    # --- LOGIN / SIGNUP ---
    st.title("🇰🇼 EcoScan Kuwait")
    if st.session_state.view == "login":
        phone = st.text_input("Mobile Number")
        pw = st.text_input("Password", type="password")
        if st.button("Log In", type="primary"):
            if phone == "admin" and pw == "admin123":
                st.session_state.user = {"name": "Founder", "phone": "admin", "area": "Kuwait City", "role": "admin"}
                st.rerun()
            users = load_data(USER_DB)
            u = next((u for u in users if u['phone'] == phone and u['password'] == pw), None)
            if u: st.session_state.user = u; st.rerun()
            else: st.error("Verification Error")
        if st.button("Register New Account"): st.session_state.view = "signup"; st.rerun()
    else:
        n = st.text_input("Full Name")
        p = st.text_input("Mobile Number")
        a = st.selectbox("Governorate", ["Asimah", "Hawalli", "Farwaniya", "Ahmadi", "Jahra", "Mubarak"])
        pw_n = st.text_input("Create Password", type="password")
        if st.button("Join & Get 10 Points"):
            if n and p and pw_n:
                users = load_data(USER_DB)
                users.append({"name": n, "phone": p, "area": a, "password": pw_n, "points": 10})
                save_data(USER_DB, users)
                st.success("Account Created! You can now log in.")
                st.session_state.view = "login"; st.rerun()
