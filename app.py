import streamlit as st
import sqlite3
import pandas as pd
import time
import uuid
import re

# --- 1. Database Functions ---
def init_db():
    conn = sqlite3.connect('marketplace.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, phone TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, user TEXT, title TEXT, description TEXT, price REAL, contact TEXT, image_path TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments (id TEXT PRIMARY KEY, item_id TEXT, user TEXT, comment TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('marketplace.db', check_same_thread=False)

def sanitize_phone(phone_number, country_code):
    if not phone_number: return None
    clean_num = re.sub(r'\D', '', phone_number)
    clean_code = re.sub(r'\D', '', country_code)
    if clean_num.startswith(clean_code): return clean_num
    else: return clean_code + clean_num

def signup_user(username, password, phone, country_code):
    conn = get_db_connection()
    c = conn.cursor()
    final_phone = sanitize_phone(phone, country_code)
    try:
        c.execute("INSERT INTO users (username, password, phone) VALUES (?, ?, ?)", (username, password, final_phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_login(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT password, phone FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == password: return result[1]
    return None

def create_item(user, title, description, price, contact, image):
    conn = get_db_connection()
    c = conn.cursor()
    item_id = str(uuid.uuid4())
    image_name = image.name if image else "placeholder.png"
    
    sql = "INSERT INTO items (id, user, title, description, price, contact, image_path) VALUES (?, ?, ?, ?, ?, ?, ?)"
    val = (item_id, user, title, description, price, contact, image_name)
    c.execute(sql, val)
    conn.commit()
    conn.close()

def get_items():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM items ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def add_comment(item_id, user, comment_text):
    conn = get_db_connection()
    c = conn.cursor()
    comment_id = str(uuid.uuid4())
    
    sql = "INSERT INTO comments (id, item_id, user, comment) VALUES (?, ?, ?, ?)"
    val = (comment_id, item_id, user, comment_text)
    c.execute(sql, val)
    conn.commit()
    conn.close()

def get_comments(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    sql = "SELECT user, comment, timestamp FROM comments WHERE item_id=? ORDER BY timestamp ASC"
    c.execute(sql, (item_id,))
    
    data = c.fetchall()
    conn.close()
    return data

# --- 2. Helper Components ---

# This decorator creates a modal popup
@st.dialog("👋 Welcome from the Founder")
def show_welcome_modal():
    c1, c2 = st.columns([1, 2])
    with c1:
        try:
            st.image("founder.jpeg", use_container_width=True)
        except:
            st.write("📷")
    with c2:
        st.write("**Hello & Welcome!**")
        st.write("We built this platform to make buying and selling simple, transparent, and direct for our community.")
        st.caption("— Digital Endurance Team")
    
    st.divider()
    if st.button("Continue to App", type="primary", use_container_width=True):
        st.session_state['has_seen_welcome'] = True
        st.rerun()

# --- 3. Main App Logic ---

def main():
    st.set_page_config(page_title="EcoScan Market", page_icon="📱", layout="wide")
    
    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    init_db()

    # --- SESSION TIMEOUT LOGIC ---
    TIMEOUT_SECONDS = 1800 
    if 'last_active' not in st.session_state:
        st.session_state['last_active'] = time.time()
    if time.time() - st.session_state['last_active'] > TIMEOUT_SECONDS:
        st.session_state.clear()
        st.session_state['last_active'] = time.time()
        st.rerun()
    st.session_state['last_active'] = time.time()

    # Initialize Session State
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['user_phone'] = None
    
    # State for Welcome Modal
    if 'has_seen_welcome' not in st.session_state:
        st.session_state['has_seen_welcome'] = False

    # Show Welcome Modal ONLY if not seen yet
    if not st.session_state['has_seen_welcome']:
        show_welcome_modal()

    # ==============*
