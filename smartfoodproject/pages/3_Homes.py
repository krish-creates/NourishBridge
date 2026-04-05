import streamlit as st
import sqlite3
import pandas as pd

# --- 1. ACCESS CONTROL ---
if 'user' not in st.session_state or st.session_state.get('role') != 'Homes':
    st.set_page_config(page_title="Access Denied", layout="centered")
    st.error("🚫 Access Denied. Please authenticate as a verified Welfare Home.")
    if st.button("Go to Login Portal"):
        st.switch_page("pages/Registration.py")
    st.stop()

# --- 2. GLOBAL PAGE CONFIG ---
st.set_page_config(page_title=f"NourishBridge | {st.session_state['user']}", layout="wide", initial_sidebar_state="collapsed")

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
        .food-card {{
            background: white; padding: 25px; border-radius: 15px;
            border: 1px solid #EAE9E4; margin-bottom: 20px;
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
        <div style='font-size: 14px; color: #666;'> <b>{st.session_state['user']}</b></div>
    </div>
""", unsafe_allow_html=True)

nav_col1, nav_col2 = st.columns([5, 1])
with nav_col2:
    if st.button("🚪 Logout", key="home_logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# --- 5. MAIN CONTENT ---
st.title("Welfare Home Dashboard")
st.divider()

tab_browse, tab_history = st.tabs(["🍱 Browse Food", "📋 Request History"])

with tab_browse:
    # --- SUCCESS STATE LOGIC ---
    if 'request_submitted' not in st.session_state:
        st.session_state.request_submitted = False

    if st.session_state.request_submitted:
        st.markdown("""
            <div style='text-align: center; padding: 60px 20px;'>
                <h1 style='font-size: 60px;'>✅</h1>
                <h2 style='color: #2E5A48;'>Request Sent Successfully!</h2>
                <p>You can track your food in 'Request History'.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Browse More Food", use_container_width=True):
            st.session_state.request_submitted = False
            st.rerun()

    else:
        # LOGIC MODIFICATION: Join with requests table to exclude already requested items
        # We only show food where THIS home hasn't already made a pending request
        query = """
            SELECT f.* FROM food f
            WHERE f.status='available' AND f.quantity > 0
            AND f.id NOT IN (
                SELECT food_id FROM requests 
                WHERE home = ? AND status IN ('Pending Approval', 'Pending Pickup')
            )
        """
        available_food = run_query(query, (st.session_state['user'],))

        if available_food.empty:
            st.info("No new food listings available. You have either requested everything or the stock is empty!")
        else:
            for i in range(0, len(available_food), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(available_food):
                        row = available_food.iloc[i + j]
                        f_id = int(row['id'])
                        with cols[j]:
                            st.markdown(f"""
                                <div class='food-card'>
                                    <div style='color: #2E5A48; font-weight: 700;'>🍴 {row['restaurant']}</div>
                                    <h3 style='margin: 10px 0;'>{row['type'].split(':')[0]}</h3>
                                    <p style='color:#555;'>📍 {row['location']}</p>
                                    <p style='font-weight: 700; color: #1B3C33;'>📦 Stock: {row['quantity']} portions</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander(f"Request from {row['restaurant']}"):
                                req_qty = st.number_input("Portions needed", min_value=1, max_value=int(row['quantity']), key=f"req_{f_id}")
                                if st.button("Submit Request", key=f"btn_{f_id}", use_container_width=True):
                                    run_cmd("""
                                        INSERT INTO requests (food_id, home, requested_qty, status) 
                                        VALUES (?, ?, ?, 'Pending Approval')
                                    """, (f_id, st.session_state['user'], req_qty))
                                    st.session_state.request_submitted = True
                                    st.rerun()

with tab_history:
    st.subheader("Your Request Timeline")
    my_requests = run_query("""
        SELECT r.status, r.requested_qty, f.restaurant, f.type 
        FROM requests r 
        JOIN food f ON r.food_id = f.id 
        WHERE r.home = ? ORDER BY r.id DESC
    """, (st.session_state['user'],))

    if my_requests.empty:
        st.info("No request history yet.")
    else:
        for _, req in my_requests.iterrows():
            status_color = "#D4A017" # Pending
            if req['status'] == 'Delivered': status_color = "#2E7D5B"
            if req['status'] == 'Pending Pickup': status_color = "#3498DB"
            
            st.markdown(f"""
                <div style='background: white; padding: 15px; border-radius: 10px; border-left: 5px solid {status_color}; margin-bottom: 10px; border: 1px solid #EEE;'>
                    <b>{req['requested_qty']} Portions</b> from {req['restaurant']} 
                    <span style='float:right; color:{status_color}; font-weight:700;'>{req['status'].upper()}</span>
                </div>
            """, unsafe_allow_html=True)