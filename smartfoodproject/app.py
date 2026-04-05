import streamlit as st
import sqlite3
import pandas as pd

# --- 1. GLOBAL PAGE CONFIG (SIDEBAR REMOVED) ---
st.set_page_config(
    page_title="NourishBridge | Ending Food Waste", 
    page_icon="🌱", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. DATABASE ARCHITECT (ISO & EARNINGS SUPPORT) ---
def upgrade_db():
    conn = sqlite3.connect('food_hero.db')
    c = conn.cursor()
    
    # 1. Users Table (With ISO support and NGO Earnings)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, 
                  username TEXT UNIQUE, 
                  password TEXT, 
                  role TEXT, 
                  display_name TEXT, 
                  location TEXT, 
                  is_approved INTEGER DEFAULT 0,
                  earnings REAL DEFAULT 0.0,
                  iso_doc TEXT)''') # New column for ISO certification path/name
    
    # 2. Food Listings Table
    c.execute('''CREATE TABLE IF NOT EXISTS food 
                 (id INTEGER PRIMARY KEY, 
                  restaurant TEXT, 
                  type TEXT, 
                  quantity INTEGER, 
                  status TEXT, 
                  location TEXT)''')
    
    # 3. Requests Table
    c.execute('''CREATE TABLE IF NOT EXISTS requests 
                 (id INTEGER PRIMARY KEY, 
                  food_id INTEGER, 
                  home TEXT, 
                  requested_qty INTEGER, 
                  status TEXT,
                  volunteer TEXT)''')

    # Column Check Logic (Ensures no crashes on existing databases)
    c.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'earnings' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN earnings REAL DEFAULT 0.0")
    if 'iso_doc' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN iso_doc TEXT")
                  
    conn.commit()
    conn.close() 

upgrade_db()

# --- 3. CUSTOM CSS (PROFESSIONAL BRANDING) ---
st.markdown("""
    <style>
    /* Hide Sidebar Completely */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    .stApp { background-color: #F9F8F3; }
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600&family=Inter:wght@400;600&display=swap');
    
    h1, h2, h3 { font-family: 'Source Serif 4', serif; color: #1B3C33 !important; }
    p, div { font-family: 'Inter', sans-serif; color: #4A4A4A; }

    .nav-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 0; border-bottom: 1px solid #EEE; margin-bottom: 40px;
    }
    
    .feature-card {
        background-color: white; padding: 30px; border-radius: 12px;
        border: 1px solid #F0F0F0; height: 260px; transition: 0.3s;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.02);
    }
    .feature-card:hover { transform: translateY(-5px); box-shadow: 0px 10px 20px rgba(0,0,0,0.05); }
    .icon-box { font-size: 32px; margin-bottom: 15px; }

    /* CTA Section */
    .cta-box {
        background-color: white; font-color:#2E5A48;
        padding: 80px 40px 120px 40px; border-radius: 25px;
        text-align: center; margin-top: 50px;
        
        .button-container { margin-top: -80px; padding-bottom: 50px; }
    }
    
    
    div.stButton > button {
        border-radius: 12px !important; background-color: white; height: 3.5em !important;
        font-weight: 600 !important; width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. TOP NAVIGATION ---
st.markdown("""
    <div class='nav-bar'>
        <div style='font-size: 24px; font-weight: 700; color: #1B3C33;'>🌱 NourishBridge</div>
        <div style='color: #666; font-size: 14px;'>NGO Partnered Redistribution Network</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. HERO SECTION ---
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown("<span style='background:#E8F2EE; color:#2E5A48; padding:5px 15px; border-radius:20px; font-size:14px; font-weight:600;'>EST. 2026</span>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 68px; line-height: 1.1; margin-top:10px;'>Bridge the Gap <br>Between <span style='color:#2E5A48;'>Surplus</span> <br>and <span style='color:#D4A017;'>Need</span></h1>", unsafe_allow_html=True)
    st.write("A professional ecosystem connecting restaurants with excess food to verified welfare homes via a funded volunteer network.")
    st.write("##")

with col_right:
    st.image("https://i.pinimg.com/736x/18/05/60/180560df7ed0193683cdfb2aa1085e49.jpg", use_container_width=True)

# --- 6. HOW IT WORKS ---
st.markdown("<div style='text-align: center; margin: 80px 0 40px 0;'>", unsafe_allow_html=True)
st.markdown("<h2 style='font-size: 42px;'>The NourishBridge Workflow</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

features = [
    ("🍴", "ISO Verified Posting", "Restaurants provide safety certifications before listing surplus portions."),
    ("🛡️", "Admin Audit", "Strict manual verification of all users to ensure safety and transparency."),
    ("🏠", "Partial Allocation", "Smart systems distribute food across multiple homes to maximize reach."),
    ("🚴", "Paid Delivery Heroes", "NGO-funded payouts incentivize volunteers for every successful delivery."),
    ("📍", "Map Integration", "Real-time routing for heroes from restaurant pickup to doorstep drop-off."),
    ("📊", "Impact Tracking", "Comprehensive analytics showing meals saved and community impact.")
]

for i in range(0, 6, 3):
    cols = st.columns(3)
    for j in range(3):
        with cols[j]:
            icon, title, desc = features[i+j]
            st.markdown(f"""
                <div class='feature-card'>
                    <div class='icon-box'>{icon}</div>
                    <h3 style='font-size:20px;'>{title}</h3>
                    <p style='font-size:15px; line-height:1.5;'>{desc}</p>
                </div>
            """, unsafe_allow_html=True)

# --- 7. FINAL CTA ---
st.markdown("""
<div class="cta-box">
    <div style='font-size: 42px; font-weight: 700; margin-bottom: 10px;'>Ready to Make a Difference?</div>
    <div style='font-size: 19px; opacity: 0.9;'>Join our network of audited partners working together to end food waste.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="button-container">', unsafe_allow_html=True)
_, btn_col1, btn_col2, _ = st.columns([2, 2, 2, 2])

with btn_col1:
    if st.button("📝 Register Now", type="primary"):
        st.switch_page("pages/signup.py")
with btn_col2:
    if st.button("🔑 Login Portal", type="secondary"):
        st.switch_page("pages/Registration.py")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<p class='footer-text' style='text-align:center; color:#888; padding: 40px 0;'>© 2026 NourishBridge Platform. All Rights Reserved.</p>", unsafe_allow_html=True)