import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- STEP 1: GOOGLE VERIFICATION (Must be the VERY first thing) ---
# We write this as plain text so the Google bot can find it instantly.
st.write("google-site-verification: UbGI9p25Kivjr9u465NRYSpRTy4euChN-XFrwiy3r40")

# Hidden tag for extra security.
GOOGLE_TAG = "UbGI9p25Kivjr9u465NRYSpRTy4euChN-XFrwiy3r40"
st.markdown(f'<head><meta name="google-site-verification" content="{GOOGLE_TAG}" /></head>', unsafe_allow_html=True)

# --- STEP 2: APP CONFIG & STYLE ---
st.set_page_config(page_title="EcoScan Kuwait", page_icon="🇰🇼", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F1F8E9; }
    .main-banner {
        background-color: #2E7D32; color: white;
        padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    .founder-box {
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        border-left: 5px solid #2E7D32; margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- STEP 3: PUBLIC FOUNDER CONTENT ---
# This remains visible so Google sees a "real" site, not an empty login.
st.markdown('<div class="main-banner"><h1>KW EcoScan Kuwait</h1><p>Community Sustainability Portal</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="founder-box">
    <h3>Our Vision</h3>
    <p>"EcoScan Kuwait is more than an app; it is a movement to protect our environment 
    by sharing resources. Every swap reduces landfill waste in our beautiful country."</p>
    <p><b>— Founder: Abhilash Babu</b></p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- STEP 4: STATUS MESSAGE ---
st.success("✅ App is Live. Google Verification in Progress.")
st.info("The Member Marketplace will unlock automatically once verification is complete.")

# Logic to prevent errors while we wait for verification
if "user" not in st.session_state:
    st.session_state.user = None
