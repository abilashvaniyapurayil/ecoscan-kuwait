import streamlit as st
import sqlite3
import pandas as pd
import time
import uuid
import re

# --- 1. Database Functions ---

DB_NAME = 'marketplace_v2.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    phone_id TEXT PRIMARY KEY, 
                    password TEXT, 
                    display_name TEXT, 
                    country_code TEXT
                )''')
    
    # Items table
    c.execute('''CREATE TABLE IF NOT EXISTS items (
                    id TEXT PRIMARY KEY, 
                    owner_phone TEXT, 
                    owner_name TEXT,
                    title TEXT, 
                    description TEXT, 
                    price REAL, 
                    country_code TEXT,
                    image_path TEXT, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Comments table
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY, 
                    item_id TEXT, 
                    user_name TEXT, 
                    comment TEXT, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def sanitize_phone(phone_number):
    if not phone_number:
        return ""
    s = str(phone_number).strip()
    return re.sub(r'\D', '', s)

def signup_user(display_name, password, phone_input, country_code):
    conn = get_db_connection()
    c = conn.cursor()
    
    clean_phone = sanitize_phone(phone_input)
    clean_pass = password.strip() 
    clean_name = display_name.strip()
    
    try:
        c.execute("INSERT INTO users (phone_id, password, display_name, country_code) VALUES (?, ?, ?, ?)", 
                  (clean_phone, clean_pass, clean_name, country_code))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Duplicate phone
    finally:
        conn.close()

def check_login(phone_input, password):
    conn = get_db_connection()
    c = conn.cursor()
    
    clean_phone = sanitize_phone(phone_input)
    clean_pass = password.strip() 
    
    c.execute("SELECT display_name, country_code FROM users WHERE phone_id=? AND password=?", (clean_phone, clean_pass))
    result = c.fetchone()
    conn.close()
    
    if result:
        return {"display_name": result[0], "country_code": result[1], "phone_id": clean_phone}
    return None

def create_item(owner_phone, owner_name, title, description, price, country_code, image):
    conn = get_db_connection()
    c = conn.cursor()
    item_id = str(uuid.uuid4())
    image_name = image.name if image else "placeholder.png"
    
    sql = "INSERT INTO items (id, owner_phone, owner_name, title, description, price, country_code, image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    val = (item_id, owner_phone, owner_name, title, description, price, country_code, image_name)
    c.execute(sql, val)
    conn.commit()
    conn.close()

def get_items():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM items ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def add_comment(item_id, user_name, comment_text):
    conn = get_db_connection()
    c = conn.cursor()
    comment_id = str(uuid.uuid4())
    
    sql = "INSERT INTO comments (id, item_id, user_name, comment) VALUES (?, ?, ?, ?)"
    val = (comment_id, item_id, user_name, comment_text)
    c.execute(sql, val)
    conn.commit()
    conn.close()

def get_comments(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    sql = "SELECT user_name, comment, timestamp FROM comments WHERE item_id=? ORDER BY timestamp ASC"
    c.execute(sql, (item_id,))
    data = c.fetchall()
    conn.close()
    return data

# --- 2. Helper Components ---

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
        st.write("We built this platform to make buying and selling simple, transparent, and direct.")
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

    # --- SESSION TIMEOUT ---
    TIMEOUT_SECONDS = 1800 
    if 'last_active' not in st.session_state:
        st.session_state['last_active'] = time.time()
    if time.time() - st.session_state['last_active'] > TIMEOUT_SECONDS:
        st.session_state.clear()
        st.session_state['last_active'] = time.time()
        st.rerun()
    st.session_state['last_active'] = time.time()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user_phone_id'] = None
        st.session_state['display_name'] = None
        st.session_state['country_code'] = None
    
    if 'has_seen_welcome' not in st.session_state:
        st.session_state['has_seen_welcome'] = False

    if not st.session_state['has_seen_welcome'] and not st.session_state['logged_in']:
        show_welcome_modal()

    # =========================================================
    # VIEW A: LOGGED OUT
    # =========================================================
    if not st.session_state['logged_in']:
        
        st.write("") 
        st.write("") 

        c_left, c_center, c_right = st.columns([1, 2, 1])
        
        with c_center:
            st.markdown("<h1 style='text-align: center;'>📱 EcoScan Market</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Secure. Simple. Local.</p>", unsafe_allow_html=True)
            
            st.divider()
            
            tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])
            
            # --- LOGIN TAB ---
            with tab_login:
                st.write("")
                st.info("Log in with your Mobile Number (No Country Code).")
                
                login_phone = st.text_input("Mobile Number (e.g., 55512345)", key="login_phone")
                login_pass = st.text_input("Password", type="password", key="login_pass")
                st.write("")
                
                if st.button("Log In", use_container_width=True):
                    user_data = check_login(login_phone, login_pass)
                    if user_data:
                        st.session_state['logged_in'] = True
                        st.session_state['user_phone_id'] = user_data['phone_id']
                        st.session_state['display_name'] = user_data['display_name']
                        st.session_state['country_code'] = user_data['country_code']
                        st.session_state['has_seen_welcome'] = True
                        st.rerun()
                    else:
                        st.error("Incorrect Number or Password. Did you include the country code by mistake?")
            
            # --- SIGN UP TAB ---
            with tab_signup:
                st.write("")
                st.caption("Create your account")
                new_name = st.text_input("Display Name (e.g., John Doe)")
                new_pass = st.text_input("New Password", type="password")
                
                c_code, c_num = st.columns([1, 2])
                with c_code:
                    country_code = st.selectbox("Code", ["+965", "+966", "+971", "+974", "+20", "+1", "+44"])
                with c_num:
                    new_phone = st.text_input("Mobile Number (No Country Code)")
                
                st.write("")

                if st.button("Create Account", use_container_width=True):
                    if new_name and new_pass and new_phone:
                        success = signup_user(new_name, new_pass, new_phone, country_code)
                        if success:
                            st.success("Account created! Please switch to the Login tab.")
                        else:
                            st.error(f"The number {new_phone} is already registered.")
                    else:
                        st.warning("Please fill all fields.")

    # =========================================================
    # VIEW B: LOGGED IN
    # =========================================================
    else:
        tab1, tab2, tab3, tab_logout, tab_about = st.tabs(["🛍️ Buy", "➕ Sell", "👤 Profile", "🚪 Log Out", "ℹ️ About Us"])

        # -- TAB 1: BUY ITEMS --
        with tab1:
            st.subheader("Latest Listings")
            search_query = st.text_input("🔍 Search items...", "")
            items = get_items()
            
            if search_query:
                items = items[items['title'].str.contains(search_query, case=False, na=False)]

            if items.empty:
                st.info("No items found.")
            else:
                for index, row in items.iterrows():
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 3])
                        with c1:
                            st.image("https://via.placeholder.com/150?text=Item", use_container_width=True)
                        with c2:
                            st.subheader(row['title'])
                            st.write(f"**{row['price']} KD**")
                            st.write(f"{row['description']}")
                            st.caption(f"Seller: {row['owner_name']}")
                            
                            if row['owner_phone'] == st.session_state['user_phone_id']:
                                st.caption("👤 *You listed this item*")
                            else:
                                full_wa_num = str(row['country_code']).replace("+","") + str(row['owner_phone'])
                                wa_message = f"Hi, I am interested in: {row['title']}"
                                wa_link = f"https://wa.me/{full_wa_num}?text={wa_message.replace(' ', '%20')}"
                                st.link_button("Chat on WhatsApp 💬", wa_link, type="primary")

                            with st.expander("View Offers / Comments"):
                                existing_comments = get_comments(row['id'])
                                for c_user, c_text, c_time in existing_comments:
                                    st.text(f"{c_user}: {c_text}")
                                
                                new_comment = st.text_input("Comment:", key=f"c_{row['id']}")
                                if st.button("Post", key=f"btn_{row['id']}"):
                                    add_comment(row['id'], st.session_state['display_name'], new_comment)
                                    st.success("Posted!")
                                    time.sleep(1)
                                    st.rerun()

        # -- TAB 2: SELL ITEM --
        with tab2:
            st.header("List Item")
            with st.form("sell_form", clear_on_submit=True):
                title = st.text_input("Title")
                desc = st.text_area("Description")
                price = st.number_input("Price (KD)", min_value=0.0, step=0.5)
                photo = st.file_uploader("Photo", type=['png', 'jpg', 'jpeg'])
                
                if st.form_submit_button("Publish", use_container_width=True):
                    if title and price > 0:
                        create_item(
                            st.session_state['user_phone_id'], 
                            st.session_state['display_name'], 
                            title, 
                            desc, 
                            price, 
                            st.session_state['country_code'], 
                            photo
                        )
                        st.balloons()
                        st.success("Listed successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Title & Price required.")

        # -- TAB 3: PROFILE --
        with tab3:
            st.header("My Profile")
            st.write(f"**Name:** {st.session_state['display_name']}")
            st.write(f"**Mobile (ID):** {st.session_state['user_phone_id']}")
            st.write(f"**Country Code:** {st.session_state['country_code']}")
            
            st.divider()
            
            with st.expander("👋 About EcoScan", expanded=True):
                st.write("### Welcome, Community Member!")
                st.write("We built this platform to make buying and selling simple, transparent, and direct.")
                st.caption("— Digital Endurance Team")

        # -- TAB 4: LOGOUT --
        with tab_logout:
            if st.button("Confirm Logout", use_container_width=True):
                st.session_state['logged_in'] = False
                st.session_state['user_phone_id'] = None
                st.session_state['has_seen_welcome'] = False
                st.success("You have been logged out.")
                st.rerun()

        # -- TAB 5: ABOUT US --
        with tab_about:
            st.header("About Us")
            st.write("### Founders:")
            st.image("https://raw.githubusercontent.com/yourusername/yourrepo/main/founder.jpeg", width=150)  # Update with your actual GitHub image URL
            st.write("**Dr. Abhilash Babu Vaniyapurayil** - Founder")

            st.write("### Company Details:")
            st.write("EcoScan Market aims to provide a secure and user-friendly platform for buying and selling items locally.")
            st.write("Our mission is to simplify transactions and build a trusted community.")

if __name__ == "__main__":
    main()
