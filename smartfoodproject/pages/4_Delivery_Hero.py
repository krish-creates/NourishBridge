import streamlit as st
import sqlite3
import pandas as pd

# --- 1. ACCESS CONTROL ---
if 'user' not in st.session_state or st.session_state.get('role') != 'Delivery Hero':
    st.set_page_config(page_title="Access Denied", layout="centered")
    st.error("🚫 Access Denied. Please authenticate as a verified Volunteer Hero.")
    if st.button("Go to Login Portal"):
        st.switch_page("pages/Registration.py")
    st.stop()

# --- 2. GLOBAL PAGE CONFIG & SIDEBAR HIDE ---
st.set_page_config(page_title=f"Hero Hub | {st.session_state['user']}", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
    <style>
        [data-testid="stSidebarNav"] {{display: none;}}
        [data-testid="collapsedControl"] {{display: none;}}
        .stApp {{ background-color: #F9F8F3; }}
        
        .nav-bar {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 20px; background-color: white; border-bottom: 1px solid #EEE;
            margin: -60px -50px 30px -50px; height: 70px;
        }}
        
        .wallet-card {{
            background: linear-gradient(135deg, #1B3C33 0%, #2E5A48 100%);
            padding: 30px; border-radius: 20px; color: white;
            box-shadow: 0 10px 20px rgba(46, 90, 72, 0.2);
            margin-bottom: 30px;
        }}

        .delivery-card {{
            background: white; padding: 25px; border-radius: 15px;
            border-left: 8px solid #D4A017; margin-bottom: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        }}

        div.stButton > button {{
            background-color: #2E5A48 !important; color: white !important;
            border-radius: 8px !important; font-weight: 600 !important;
            border: none !important;
        }}
        div.stButton > button:hover {{ background-color: #D4A017 !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATABASE HELPERS ---
def run_query(q, params=()):
    with sqlite3.connect('food_hero.db') as conn:
        return pd.read_sql_query(q, conn, params=params)

def run_cmd(q, params=()):
    with sqlite3.connect('food_hero.db') as conn:
        cur = conn.cursor()
        cur.execute(q, params)
        conn.commit()

# --- 4. TOP NAVIGATION ---
st.markdown(f"""
    <div class='nav-bar'>
        <div style='font-size: 22px; font-weight: 700; color: #1B3C33;'>🌱 NourishBridge</div>
        <div style='font-size: 14px; color: #666;'>Hero: <b>{st.session_state['user']}</b></div>
    </div>
""", unsafe_allow_html=True)

nav_col1, nav_col2 = st.columns([5, 1])
with nav_col2:
    if st.button("🚪 Logout", key="hero_logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# --- 5. NGO WALLET SECTION ---
hero_info = run_query("SELECT earnings FROM users WHERE display_name = ?", (st.session_state['user'],))
balance = hero_info.iloc[0]['earnings'] if not hero_info.empty else 0.0

st.markdown(f"""
    <div class="wallet-card">
        <p style='margin:0; font-size: 13px; opacity: 0.8; letter-spacing: 1px;'>NGO FUNDED EARNINGS</p>
        <h1 style='margin:0; color: white !important; font-size: 48px;'>₹ {balance:.2f}</h1>
        <div style='display: flex; gap: 20px; margin-top: 20px;'>
            <div style='background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 10px; font-size: 12px;'>✓ KYC Verified</div>
            <div style='background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 10px; font-size: 12px;'>📅 Next Payout: Friday</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 6. LIVE TASK FEED ---
st.divider()
tab_available, tab_active = st.tabs(["📦 Available Tasks", "🛵 Active Deliveries"])

with tab_available:
    tasks = run_query("""
        SELECT r.id, r.requested_qty, r.home, f.restaurant, f.type, f.location as rest_loc 
        FROM requests r JOIN food f ON r.food_id = f.id 
        WHERE r.status = 'Pending Pickup' AND (r.volunteer IS NULL OR r.volunteer = '')
    """)

    if tasks.empty:
        st.info("The map is currently quiet. New tasks appear when restaurants approve home requests.")
    else:
        for _, task in tasks.iterrows():
            st.markdown(f"""
                <div class='delivery-card'>
                    <p style='color: #888; font-size: 11px; font-weight: 700; margin:0;'>SURPLUS PICKUP AVAILABLE</p>
                    <h3 style='margin: 5px 0;'>{task['restaurant']} ➔ {task['home']}</h3>
                    <p style='color: #444; font-size: 14px;'>📍 Pickup: {task['rest_loc']}<br>🍱 {task['requested_qty']} Portions of {task['type'].split(':')[0]}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Claim Task #{task['id']} (Earn ₹80)", key=f"claim_{task['id']}", use_container_width=True):
                run_cmd("UPDATE requests SET volunteer = ?, status = 'In Transit' WHERE id = ?", (st.session_state['user'], task['id']))
                st.toast("Task Claimed! Navigating to Pickup Point...")
                st.rerun()

with tab_active:
    active = run_query("""
        SELECT r.id, r.requested_qty, r.home, f.restaurant, f.type, f.location as rest_loc, u.location as home_loc
        FROM requests r 
        JOIN food f ON r.food_id = f.id 
        JOIN users u ON r.home = u.display_name
        WHERE r.volunteer = ? AND r.status = 'In Transit'
    """, (st.session_state['user'],))

    if active.empty:
        st.write("You don't have any active deliveries. Claim a task to start earning!")
    else:
        for _, act in active.iterrows():
            st.success(f"🚀 ACTIVE MISSION: Delivering to {act['home']}")
            
            # --- THE MAP INTEGRATION ---
            st.markdown("### 📍 Live Delivery Route")
            # For the demo, we show a professional map visualization
            st.image("https://i.pinimg.com/736x/8f/9b/60/8f9b60b73c683b5e9f8641b9d4f5597a.jpg", caption=f"Route: {act['rest_loc']} to {act['home_loc']}")
            
            

            with st.container():
                st.write(f"**Step 1:** Pick up {act['requested_qty']} units from **{act['restaurant']}**")
                st.write(f"**Step 2:** Deliver to **{act['home']}** at {act['home_loc']}")
                
                if st.button(f"Confirm Delivery & Earn ₹80 ✅", key=f"deliv_{act['id']}", use_container_width=True):
                    run_cmd("UPDATE requests SET status = 'Delivered' WHERE id = ?", (act['id'],))
                    run_cmd("UPDATE users SET earnings = earnings + 80.0 WHERE display_name = ?", (st.session_state['user'],))
                    st.balloons()
                    st.success("Impact Made! Check your updated wallet balance.")
                    st.rerun()

st.markdown("<p style='text-align:center; color:#888; font-size:12px; padding: 40px;'>Hero operations powered by NourishBridge NGO Logistics.</p>", unsafe_allow_html=True)