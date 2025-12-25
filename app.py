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
    if not phone_number:
        return None
    clean_num = re.sub(r'\D', '', phone_number)
    clean_code = re.sub(r'\D', '', country_code)
    if clean_num.startswith(clean_code):
        return clean_num
    else:
        return clean_code + clean_num

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
    if result and result[0] == password:
        return result[1]
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

# --- 2. Helper Components (Dialogs) ---

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
    
    if 'has_seen_welcome' not in st.session_state:
        st.session_state['has_seen_welcome'] = False

    # Show Welcome Modal ONLY if not seen yet
    if not st.session_state['has_seen_welcome']:
        show_welcome_modal()

    # =========================================================
    # VIEW A: LOGGED OUT (Clean, Centered Login)
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
            
            with tab_login:
                st.write("")
                login_user = st.text_input("Username", key="login_user")
                login_pass = st.text_input("Password", type="password", key="login_pass")
                st.write("")
                if st.button("Log In", use_container_width=True):
                    phone_found = check_login(login_user, login_pass)
                    if phone_found:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = login_user
                        st.session_state['user_phone'] = phone_found
                        st.session_state['has_seen_welcome'] = True
                        st.rerun()
                    else:
                        st.error("Incorrect username or password")
            
            with tab_signup:
                st.write("")
                new_user = st.text_input("New Username")
                new_pass = st.text_input("New Password", type="password")
                c_code, c_num = st.columns([1, 2])
                with c_code:
                    country_code = st.selectbox("Code", ["+965", "+966", "+971", "+974", "+20", "+1", "+44"])
                with c_num:
                    new_phone = st.text_input("Mobile Number")
                st.write("")

                if st.button("Sign Up", use_container_width=True):
                    if new_user and new_pass and new_phone:
                        if signup_user(new_user, new_pass, new_phone, country_code):
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username already exists.")
                    else:
                        st.warning("Please fill all fields.")

    # =========================================================
    # VIEW B: LOGGED IN (Main Screen = Listings, Sidebar = Menu)
    # =========================================================
    else:
        with st.sidebar:
            st.image("founder.jpeg", width=80)
            st.write(f"Hello, **{st.session_state['username']}**")
            st.divider()
            if st.button("Log Out", type="primary"):
                st.session_state['logged_in'] = False
                st.session_state['has_seen_welcome'] = True
                st.rerun()

        tab1, tab2, tab3 = st.tabs(["🛍️ Buy", "➕ Sell", "👤 Profile"])

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
                            
                            # --- LOGIC FIX: HIDE WHATSAPP BUTTON IF IT IS YOUR OWN ITEM ---
                            if row['user'] == st.session_state['username']:
                                st.caption("👤 *You listed this item*")
                            else:
                                wa_message = f"Hi, I am interested in: {row['title']}"
                                wa_link = f"https://wa.me/{row['contact']}?text={wa_message.replace(' ', '%20')}"
                                st.link_button("Chat on WhatsApp 💬", wa_link, type="primary")
                            # -------------------------------------------------------------

                            with st.expander("View Offers"):
                                existing_comments = get_comments(row['id'])
                                for c_user, c_text, c_time in existing_comments:
                                    st.text(f"{c_user}: {c_text}")
                                
                                new_comment = st.text_input("Your offer:", key=f"c_{row['id']}")
                                if st.button("Send", key=f"btn_{row['id']}"):
                                    add_comment(row['id'], st.session_state['username'], new_comment)
                                    st.success("Sent!")
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
                        create_item(st.session_state['username'], title, desc, price, st.session_state['user_phone'], photo)
                        st.balloons()
                        st.success("Listed!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Title & Price required.")

        # -- TAB 3: PROFILE --
        with tab3:
            st.header("My Profile")
            st.write(f"**Username:** {st.session_state['username']}")
            st.write(f"**Contact:** {st.session_state['user_phone']}")
            
            st.divider()
            
            with st.expander("👋 About EcoScan / Founder Message", expanded=True):
                c1, c2 = st.columns([1, 3])
                with c1:
                    try:
                        st.image("founder.jpeg", use_container_width=True)
                    except:
                        st.write("📷")
                with c2:
                    st.write("### Welcome, Community Member!")
                    st.write("We built this platform to make buying and selling simple, transparent, and direct.")
                    st.write("Our goal is to reduce waste and help you find great value in your local community.")
                    st.caption("— Digital Endurance Team")

if __name__ == "__main__":
    main()
