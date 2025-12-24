import streamlit as st
from PIL import Image
import pandas as pd
import json
import os

st.set_page_config(
    page_title="EcoScan Pro: Salmiya", 
    page_icon="🌱", 
    layout="wide"
)
# --- Database & Config ---
DB_FILE = "items_db.json"
st.set_page_config(page_title="EcoScan Pro: Salmiya", page_icon="🌱", layout="wide")

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    # Default data for a beautiful start
    return [
        {"name": "Bicycle", "user": "Ahmad", "lat": 29.3375, "lon": 48.0750, "eco": "22kg"},
        {"name": "Bookshelf", "user": "Fatima", "lat": 29.3420, "lon": 48.0820, "eco": "15kg"}
    ]

def save_item(name, user, lat, lon, eco):
    data = load_data()
    data.append({"name": name, "user": user, "lat": lat, "lon": lon, "eco": eco})
    with open(DB_FILE, "w") as f: json.dump(data, f)

# --- Sidebar Impact ---
data = load_data()
st.sidebar.title("🌍 Salmiya Impact")
st.sidebar.metric(label="CO2 Prevented", value=f"{5120 + (len(data)*5)} kg", delta="12%")

# SHARE BUTTON (Feature #3)
share_text = f"I just saved {5120 + (len(data)*5)}kg of CO2 using EcoScan Salmiya! 🌱"
st.sidebar.markdown(f"[![Share on WhatsApp](https://img.shields.io/badge/Share-WhatsApp-25D366?style=for-the-badge&logo=whatsapp)](https://api.whatsapp.com/send?text={share_text})")

# --- Main App ---
st.title("🌱 EcoScan & Swap")
t1, t2, t3 = st.tabs(["📤 Scan & Post", "📍 Salmiya Map", "📱 Feed"])

with t1:
    st.subheader("Post an Item")
    up = st.file_uploader("Scan item photo", type=["jpg", "png", "jpeg"])
    if up:
        st.image(Image.open(up), width=300)
        if st.button("Confirm & Post to Salmiya"):
            # Simulates a random location in Salmiya for testing
            save_item(up.name.split('.')[0], "You", 29.33 + (len(data)*0.001), 48.07 + (len(data)*0.001), "10kg")
            st.success("Item is live! Check the Map.")
            st.balloons()

with t2:
    st.subheader("Neighborhood Swap Map") # Feature #1 & #2
    map_df = pd.DataFrame(data)
    # This creates the interactive map centered on Salmiya
    st.map(map_df, latitude='lat', longitude='lon', zoom=13)
    st.info("💡 The red dots show where neighbors are ready to swap items!")

with t3:
    st.subheader("Recent Swaps")
    for item in reversed(data):
        with st.container(border=True):
            st.write(f"**{item['name']}**")
            st.caption(f"👤 Offered by: {item['user']} | 🌱 Impact: {item['eco']}")
            if st.button(f"Message about {item['name']}", key=item['name']):
                st.info("Chat feature connecting to neighbor...")

