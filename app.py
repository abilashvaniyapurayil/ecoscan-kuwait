import streamlit as st
import os

# --- 1. THE GOOGLE BACKDOOR ---
# Replace 'google12345.html' with your ACTUAL filename
verification_filename = "google12345.html" 

if os.path.exists(verification_filename):
    with open(verification_filename, "r") as f:
        html_content = f.read()
    # This creates a link Google can follow
    st.download_button("Verification Link", html_content, file_name=verification_filename)

# --- 2. YOUR FOUNDER CONTENT ---
st.set_page_config(page_title="EcoScan Kuwait", page_icon="🇰🇼")
st.markdown("""
    <style>
    .stApp { background-color: #F1F8E9; }
    .main-banner { background-color: #2E7D32; color: white; padding: 30px; border-radius: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-banner"><h1>KW EcoScan Kuwait</h1><p>Community Sustainability Portal</p></div>', unsafe_allow_html=True)

st.write("### Founder's Vision")
st.write("EcoScan Kuwait is a movement to protect our environment by sharing resources.")
