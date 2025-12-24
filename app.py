import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. GOOGLE & META VERIFICATION (THE PRO WAY) ---
# This injects your specific code directly into the app's hidden head
GOOGLE_VERIFY_TAG = '<meta name="google-site-verification" content="UbGI9p25Kivjr9u465NRYSpRTy4euChN-XFrwiy3r40" />'

# Injecting the tag
st.markdown(f'', unsafe_allow_html=True)
components.html(
    f"""
    <html>
        <head>
            {GOOGLE_VERIFY_TAG}
        </head>
        <body></body>
    </html>
    """,
    height=0,
)

# --- 2. MOBILE APP CONFIG ---
st.set_page_config(page_title="EcoScan Kuwait", page_icon="🇰🇼", layout="centered")

# --- 3. PROFESSIONAL STYLING ---
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
    .stButton>button { border-radius: 25px; width: 100%; height: 3.5em; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA ENGINE ---
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

# --- 5. SOCIAL LOGIN UI (SUPABASE READY) ---
def social_login_ui():
    st.markdown("""
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <button style="display: flex; align-items: center; justify-content: center; padding: 10px; border-radius: 10px; border: 1px solid #ddd; background: white; cursor: pointer;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_Color_Icon.svg" width="20" style="margin-right:10px;">
                Continue with Google
            </button>
        </div>
    """, unsafe_allow_html=True)

# --- 6. MAIN INTERFACE ---
if st.session_state.get("user"):
    st.markdown('<div class="main-banner"><h1>EcoScan Kuwait</h1><p>Verified Founder Portal</p></div>', unsafe_allow_html=True)
    tabs = st.tabs(["📤 Post", "📱 Feed", "🏆 Top", "⚖️ Legal"])
    
    with tabs[3]:
        st.subheader("Legal & Privacy")
        st.write("Google Verification Code: UbGI9p25Kivjr9u465NRYSpRTy4euChN-XFrwiy3r40")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()
else:
    st.title("🌱 EcoScan Kuwait")
    st.subheader("Sign in to start swapping")
    social_login_ui()
    st.write("--- OR ---")
    
    # Traditional login fallback
    phone = st.text_input("Mobile Number")
    if st.button("Continue"):
        st.session_state.user = {"name": "Founder", "phone": phone, "area": "Kuwait"}
        st.rerun()
