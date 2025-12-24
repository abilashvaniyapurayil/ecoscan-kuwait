import streamlit as st

# --- 1. GOOGLE SEARCH CONSOLE VERIFICATION (MUST BE AT THE TOP) ---
# This remains public so Google can verify your site.
GOOGLE_TAG = "UbGI9p25Kivjr9u465NRYSpRTy4euChN-XFrwiy3r40"
st.markdown(f'<head><meta name="google-site-verification" content="{GOOGLE_TAG}" /></head>', unsafe_allow_html=True)

# --- 2. APP CONFIGURATION ---
st.set_page_config(page_title="EcoScan Kuwait", page_icon="🇰🇼", layout="centered")

# --- 3. PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #F1F8E9; }
    .main-banner {
        background-color: #2E7D32; color: white;
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    .stButton>button { border-radius: 20px; width: 100%; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SECRETS VALIDATION ---
# Prevents crashing if secrets are missing.
if "auth" not in st.secrets:
    st.error("⚠️ Configuration missing. Please add your [auth] keys to Streamlit Cloud Secrets.")
    st.stop()

# --- 5. SOCIAL LOGIN LOGIC ---
if not st.user.is_logged_in:
    st.markdown('<div class="main-banner"><h1>🇰🇼 EcoScan Kuwait</h1><p>Kuwait\'s Circular Economy</p></div>', unsafe_allow_html=True)
    st.subheader("Join the community")
    
    if st.button("Continue with Google", type="primary"):
        try:
            st.login() # Triggers Google OAuth
        except Exception as e:
            st.error(f"Authentication Error: {e}")
    st.stop() 

# --- 6. PROTECTED APP CONTENT ---
st.markdown(f'<div class="main-banner"><h1>EcoScan Kuwait</h1><p>Welcome, {st.user.name}!</p></div>', unsafe_allow_html=True)
st.write(f"Logged in as: {st.user.email}")

if st.button("Log Out"):
    st.logout()
