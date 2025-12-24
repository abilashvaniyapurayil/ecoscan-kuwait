import streamlit as st
from PIL import Image
import pandas as pd
import json
import os

# 1. PAGE CONFIG
st.set_page_config(
    page_title="EcoScan Pro: Salmiya", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Database & Centers ---
DB_FILE = "items_db.json"

# Permanent Recycling Centers in Salmiya
RECYCLING_CENTERS = [
    {"name": "Salmiya Block 4 Drop-off", "user": "OFFICIAL CENTER", "lat": 29.3325, "lon": 48.0680, "eco": "Unlimited", "cat": "Recycling"},
    {"name": "Salmiya Co-op Collection", "user": "OFFICIAL CENTER", "lat": 29.3415, "lon": 48.0730, "eco": "Unlimited", "cat": "Recycling"}
]

def load_data():
    user_data = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: user_data = json.load(f)
    else:
        user_data = [
            {"name": "Bicycle", "user": "Ahmad", "lat": 29.3375, "lon": 48.0750, "eco": "22kg", "cat": "Sports"},
            {"name": "Bookshelf", "user": "Fatima", "lat": 29.3420, "lon": 48.0820, "eco": "15kg", "cat": "Furniture"}
        ]
    return user_data + RECYCLING_CENTERS # Combine user items with official centers

def save_item(name, user, lat, lon, eco, cat):
    # We only save user items to the JSON file, not the permanent centers
    current_data = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: current_data = json.load(f)
    current_data.append({"name": name, "user": user, "lat": lat, "lon": lon, "eco": eco, "cat": cat})
    with open(DB_FILE, "w") as f: json.dump(current_data, f)

# --- Sidebar ---
data = load_data()
st.sidebar.title("🌍 Salmiya Impact")
user_items_count = len([d for d in data if d['user'] != "OFFICIAL CENTER"])
st.sidebar.metric(label="CO2 Prevented", value=f"{5120 + (user_items_count*5)} kg", delta="12%")

# Sharing Feature
share_text = f"I just saved {5120 + (user_items_count*5)}kg of CO2 using EcoScan Salmiya! 🌱"
st.sidebar.markdown(f"[![Share on WhatsApp](https://img.shields.io/badge/Share-WhatsApp-25D366?style=for-the-badge&logo=whatsapp)](https://api.whatsapp.com/send?text={share_text})")

st.sidebar.subheader("🔍 Filter Map")
categories = ["All", "Furniture", "Electronics", "Clothes", "Sports", "Recycling"]
selected_cat = st.sidebar.selectbox("Show me:", categories)

# Filter Logic
if selected_cat == "All":
    filtered_data = data
else:
    filtered_data = [d for d in data if d.get('cat') == selected_cat]

# --- Main App ---
st.title("🌱 EcoScan & Swap")
t1, t2, t3 = st.tabs(["📤 Scan & Post", "📍 Salmiya Map", "📱 Feed"])

with t1:
    st.subheader("Post an Item")
    item_cat = st.selectbox("Category", [c for c in categories if c not in ["All", "Recycling"]])
    up = st.file_uploader("Scan item photo", type=["jpg", "png", "jpeg"])
    if up:
        st.image(Image.open(up), width=300)
        if st.button("Confirm & Post"):
            save_item(up.name.split('.')[0], "You", 29.33 + (user_items_count*0.001), 48.07 + (user_items_count*0.001), "10kg", item_cat)
            st.success("Posted! Visit the map to see your green dot.")
            st.balloons()

with t2:
    st.subheader(f"Salmiya Map: {selected_cat}")
    if not filtered_data:
        st.warning("No items in this category.")
    else:
        map_df = pd.DataFrame(filtered_data)
        # 🟡 Yellow for centers, 🔵 Blue for neighbors, 🟢 Green for You
        def get_color(user):
            if user == "OFFICIAL CENTER": return '#FFFF00'
            if user == "You": return '#00FF00'
            return '#0000FF'
            
        map_df['color'] = map_df['user'].apply(get_color)
        st.map(map_df, latitude='lat', longitude='lon', color='color', zoom=13)
        st.markdown("🟡 **Yellow:** Recycling Center | 🔵 **Blue:** Neighbor Swap | 🟢 **Green:** Your Post")

with t3:
    st.subheader("Neighborhood Feed")
    # Only show swap items in the feed, not the recycling centers
    swaps_only = [d for d in filtered_data if d['user'] != "OFFICIAL CENTER"]
    for item in reversed(swaps_only):
        with st.container(border=True):
            st.write(f"**{item['name']}** ({item['cat']})")
            st.caption(f"👤 {item['user']} | 🌱 {item['eco']} Saved")
            st.button("Message Neighbor", key=f"feed_{item['name']}")
