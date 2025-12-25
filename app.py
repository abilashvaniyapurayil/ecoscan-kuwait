import streamlit as st
import pandas as pd
import json
import os
import base64
import urllib.parse
from PIL import Image
from io import BytesIO
from datetime import datetime

# --- 1. CONFIG & APP STORE META ---
st.set_page_config(page_title="EcoScan Kuwait", page_icon="🌱", layout="centered")

# CSS to make it look like a mobile app
st.markdown("""
    <style>
    .stApp { background-color: #F1F8E9; }
    .main-banner {
        background-color: #2E7D32; color: white; padding: 20px;
        border-radius: 15px; text-align: center; margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    .profile-card {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE ---
USER_DB = "users_db.json"
ITEM_DB = "items_db.json"

# Common Country Codes for Kuwait Expats
COUNTRY_CODES = [
    "+965 (Kuwait)", 
    "+966 (Saudi Arabia)", 
    "+971 (UAE)", 
    "+974 (Qatar)", 
    "+973 (Bahrain)",
    "+968 (Oman)",
    "+20 (Egypt)", 
    "+91 (India)", 
    "+63 (Philippines)", 
    "+880 (Bangladesh)", 
    "+92 (Pakistan)",
    "+961 (Lebanon)",
    "+962 (Jordan)",
    "+1 (USA/Canada)",
    "+44 (UK)",
    "Other"
]

def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def image_to_base64(image_file):
    if image_file:
        return base64.b64encode(image_file.getvalue()).decode()
    return None

def base64_to_image(base64_string):
    if base64_string:
        try: return Image.open(BytesIO(base64.b64decode(base64_string)))
        except: return None
    return None

# Helper: Extract just the numbers for the WhatsApp Link
def clean_phone_for_wa(full_phone_string):
    # This turns "+965 12345678" into "96512345678"
    return ''.join(filter(str.isdigit, str(full_phone_string)))

# --- 3. SESSION LOGIC ---
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "login"

# --- 4. APP CONTENT ---
if st.session_state.user:
    # --- LOGGED IN AREA ---
    is_admin = st.session_state.user.get("role") == "admin"
    st.markdown(f'<div class="main-banner"><h1>EcoScan Kuwait</h1><p>Welcome, {st.session_state.user["name"]}</p></div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📤 Post Item", "📱 Community Feed", "👤 Profile"])

    # --- TAB 1: POST ITEM ---
    with tabs[0]:
        st.subheader("List an Item")
        with st.form("post_form", clear_on_submit=True):
            i_name = st.text_input("Item Name")
            i_cat = st.selectbox("Category", ["Furniture", "Electronics", "Clothing", "Books", "Vehicles", "Other"])
            i_desc = st.text_area("Description")
            i_image = st.file_uploader("Add Photo", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("Post to Marketplace"):
                if i_name:
                    items = load_data(ITEM_DB)
                    img_str = image_to_base64(i_image)
                    
                    new_item = {
                        "id": str(datetime.now().timestamp()), 
                        "name": i_name, 
                        "cat": i_cat,
                        "desc": i_desc,
                        "image": img_str,
                        "user": st.session_state.user['name'],
                        "phone": st.session_state.user['phone'], 
                        "area": st.session_state.user['area'],
                        "messages": [] 
                    }
                    items.append(new_item)
                    save_data(ITEM_DB, items)
                    st.success("Item posted successfully!")
                else:
                    st.error("Item name is required.")

    # --- TAB 2: FEED (CHAT & OFFERS) ---
    with tabs[1]:
        st.subheader("Marketplace")
        search_query = st.text_input("🔍 Search items...", key="search_main")
        
        items = load_data(ITEM_DB)
        if not items: st.info("No items yet.")
        
        if search_query:
            items = [i for i in items if search_query.lower() in i['name'].lower()]

        for i in reversed(items):
            with st.container(border=True):
                if i.get("image"):
                    st.image(base64_to_image(i["image"]), use_container_width=True)
                
                st.write(f"### {i['name']}")
                st.write(f"**Category:** {i['cat']} | **Area:** {i['area']}")
                if i.get("desc"): st.caption(i["desc"])
                st.caption(f"Posted by: {i['user']}")

                col1, col2 = st.columns(2)
                
                # Button A: WhatsApp Direct
                with col1:
                    raw_phone = i.get('phone', '')
                    clean_wa = clean_phone_for_wa(raw_phone)
                    
                    if clean_wa:
                        msg_text = urllib.parse.quote(f"Hi, I am interested in your {i['name']} on EcoScan.")
                        wa_link = f"https://wa.me/{clean_wa}?text={msg_text}"
                        st.link_button("🟢 WhatsApp", wa_link, use_container_width=True)
                    else:
                        st.button("No Phone", disabled=True)

                # Button B: Internal Comments
                with col2:
                    with st.expander(f"💬 Offers ({len(i.get('messages', []))})"):
                        for m in i.get('messages', []):
                            st.caption(f"**{m['by']}**: {m['text']}")
                        
                        offer_text = st.text_input("Comment", key=f"input_{i['id']}")
                        if st.button("Send", key=f"btn_{i['id']}"):
                            if offer_text:
                                all_items = load_data(ITEM_DB)
                                for idx, db_item in enumerate(all_items):
                                    if db_item['id'] == i['id']:
                                        if "messages" not in db_item: db_item["messages"] = []
                                        db_item["messages"].append({
                                            "by": st.session_state.user['name'],
                                            "text": offer_text
                                        })
                                        all_items[idx] = db_item
                                        save_data(ITEM_DB, all_items)
                                        st.rerun()

                if is_admin:
                    if st.button("🗑️ Delete", key=f"del_{i['id']}"):
                        items = [x for x in load_data(ITEM_DB) if x['id'] != i['id']]
                        save_data(ITEM_DB, items)
                        st.rerun()

    # --- TAB 3: PROFILE & LOGOUT ---
    with tabs[2]:
        st.subheader("Your Profile")
        st.markdown(f"""
        <div class="profile-card">
            <h3>👤 {st.session_state.user['name']}</h3>
            <p><b>📍 Area:</b> {st.session_state.user['area']}</p>
            <p><b>📞 Contact:</b> {st.session_state.user['phone']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Log Out"):
            st.session_state.user = None
            st.rerun()

else:
    # --- LOGIN / SIGNUP SCREEN ---
    st.markdown('<div class="main-banner"><h1>🌱 EcoScan Kuwait</h1></div>', unsafe_allow_html=True)
    
    if st.session_state.view == "login":
        st.subheader("Login")
        
        # Login with Code Selector
        col_l1, col_l2 = st.columns([1, 2])
        with col_l1:
            l_code = st.selectbox("Code", COUNTRY_CODES, index=0, label_visibility="collapsed")
        with col_l2:
            l_num = st.text_input("Phone Number", label_visibility="collapsed", placeholder="e.g. 12345678")
            
        u_pw = st.text_input("Password", type="password")
        
        if st.button("Sign In", type="primary"):
            # Construct full phone for checking
            full_login_phone = l_code.split(" ")[0] + l_num
            
            # Admin Backdoor
            if l_num == "90000000" and u_pw == "founder2025":
                st.session_state.user = {"name": "Founder", "phone": "+96590000000", "area": "Kuwait City", "role": "admin"}
                st.rerun()
                
            users = load_data(USER_DB)
            # Find user matching exact phone string
            u = next((x for x in users if x['phone'] == full_login_phone and x['password'] == u_pw), None)
            
            if u: 
                st.session_state.user = u
                st.rerun()
            else: 
                # Fallback: Try checking just the number in case old users exist
                u_alt = next((x for x in users if l_num in x['phone'] and x['password'] == u_pw), None)
                if u_alt:
                    st.session_state.user = u_alt
                    st.rerun()
                else:
                    st.error("Invalid phone or password.")
                    
        if st.button("Create Account"):
            st.session_state.view = "signup"
            st.rerun()
        
    else:
        st.subheader("Create Account")
        with st.form("signup_form"):
            s_name = st.text_input("Full Name")
            
            # Country Code Selector for Signup
            st.write("WhatsApp Number")
            col_s1, col_s2 = st.columns([1, 2])
            with col_s1:
                s_code = st.selectbox("Country Code", COUNTRY_CODES, index=0) # Default +965
            with col_s2:
                s_num = st.text_input("Mobile Number", placeholder="e.g. 12345678")
                
            s_area = st.selectbox("Area", ["Kuwait City", "Salmiya", "Hawalli", "Jahra", "Fahaheel", "Mangaf", "Other"])
            s_pw = st.text_input("Create Password", type="password")
            
            if st.form_submit_button("Register"):
                if s_name and s_num and s_pw:
                    # Combine Code and Number: e.g. "+965" + "12345678" -> "+96512345678"
                    # We strip the country name text from the selectbox first (e.g. " (Kuwait)")
                    clean_code = s_code.split(" ")[0]
                    full_phone = clean_code + s_num
                    
                    users = load_data(USER_DB)
                    if any(u['phone'] == full_phone for u in users):
                        st.error("Number already registered.")
                    else:
                        users.append({"name": s_name, "phone": full_phone, "area": s_area, "password": s_pw, "role": "user"})
                        save_data(USER_DB, users)
                        st.success("Account created! Go to login.")
                        st.session_state.view = "login"
                        st.rerun()
                else: 
                    st.warning("Please fill all fields.")
        
        if st.button("Back to Login"):
            st.session_state.view = "login"
            st.rerun()
