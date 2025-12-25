import streamlit as st
import sqlite3
import pandas as pd
import time
import uuid
import re

# --- 1. Database Functions (Unchanged) ---
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
    c.execute("INSERT INTO items (id, user, title, description, price, contact, image_path) VALUES (?, ?, ?, ?, ?, ?, ?)", (item_id, user, title, description, price, contact, image_name))
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
    c.execute("INSERT INTO comments (id, item_id, user, comment) VALUES (?, ?, ?, ?)", (comment_id, item_id, user, comment_text))
    conn.commit()
    conn.close()

def get_comments(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT user, comment, timestamp FROM comments WHERE item_id=? ORDER BY timestamp ASC", (item_id,))
    data = c.fetchall()
    conn.close()
    return data

# --- 2. Main App Logic ---

def main():
    st.set_page_config(page_title="EcoScan Market", page_icon="📱", layout="wide")
    
    # CSS to hide default menu but keep app clean
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

    # Session State
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['user_phone'] = None

    # ======================================================
    # CASE 1: USER IS NOT LOGGED IN (Welcome Screen)
    # ======================================================
    if not st.session_state['logged_in']:
        
        # Center the Logo/Title
        st.title("📱 EcoScan Market")
        st.subheader("Welcome to the Community!")

        # Create two columns for layout on desktop, stacks on mobile
        col1, col2 = st.columns([1, 1])

        with col1:
            st.info("Please Login or Sign Up to view the market.")
            tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])
            
            with tab_login:
                login_user = st.text_input("Username", key="login_user")
                login_pass = st.text_input("Password", type="password", key="login_pass")
                if st.button("Log In", use_container_width=True):
                    phone_found = check_login(login_user, login_pass)
                    if phone_found:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = login_user
                        st.session_state['user_phone'] = phone_found
                        st.rerun()
                    else:
                        st.error("Incorrect username or password")
            
            with tab_signup:
                new_user = st.text_input("New Username")
                new_pass = st.text_input("New Password", type="password")
                c_code, c_num = st.columns([1, 2])
                with c_code:
                    country_code = st.selectbox("Code", ["+965", "+966", "+971", "+974", "+20", "+1", "+44"])
                with c_num:
                    new_phone = st.text_input("Mobile Number")

                if st.button("Sign Up", use_container_width=True):
                    if new_user and new_pass and new_phone:
                        if signup_user(new_user, new_pass, new_phone, country_code):
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username already exists.")
                    else:
                        st.warning("Please fill all fields.")

        # Founder Message - Visible on Home Screen now!
        with col2:
            st.markdown("---")
            st.subheader("👋 From the Founder")
            try:
                # Using a smaller width for better mobile fit
                st.image("founder.jpeg", width=200, caption="Founder's Note") 
            except:
                st.info("(founder.jpeg not found)")
            st.write("Welcome to our community! We built this platform to make buying and selling simple, transparent, and direct. Thank you for being a part of our journey.")

    # ======================================================
    # CASE 2: USER IS LOGGED IN (Main App Interface)
    # ======================================================
    else:
        # Sidebar is ONLY used for Logout and Profile info when logged in
        with st.sidebar:
            st.image("founder.jpeg", width=100)
            st.write(f"Logged in as: **{st.session_state['username']}**")
            if st.button("Log Out"):
                st.session_state['logged_in'] = False
                st.rerun()

        # Main Content Tabs
        tab1, tab2, tab3 = st.tabs(["🛍️ Buy", "➕ Sell", "👤 Profile"])

        # -- TAB 1: BUY ITEMS --
        with tab1:
            st.subheader("Latest Listings")
            search_query = st.text_input("🔍 Search items...", "")
            items = get_items()
            
            if search_query:*
