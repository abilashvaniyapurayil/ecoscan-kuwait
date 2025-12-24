import streamlit as st

# MUST be the first line
st.set_page_config(page_title="EcoScan Kuwait", page_icon="🇰🇼")

# --- STEP 1: DEDICATED VERIFICATION URL ---
# This creates a "hidden" path that Google's bot can follow easily.
query_params = st.query_params
if "verify" in query_params:
    st.write("google-site-verification: UbGI9p25Kivjr9u465NRYSpRTy4euChN-XFrwiy3r40")
    st.stop() # Stops the rest of the page from loading for the bot

# --- STEP 2: PROFESSIONAL CONTENT ---
st.markdown("""
    <style>
    .stApp { background-color: #F1F8E9; }
    .main-banner {
        background-color: #2E7D32; color: white;
        padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    </style>
    <div class="main-banner">
        <h1>KW EcoScan Kuwait</h1>
        <p>Community Sustainability Portal</p>
    </div>
    """, unsafe_allow_html=True)

st.success("✅ Verification System Active.")
st.write("### Founder's Vision")
st.info("EcoScan Kuwait is a movement to protect our environment by sharing resources.")

# Injects the tag into the main header as well
st.markdown('<meta name="google-site-verification" content="UbGI9p25Kivjr9u465NRYSpRTy4euChN-XFrwiy3r40" />', unsafe_allow_html=True)
