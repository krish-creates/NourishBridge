import streamlit as st
import sqlite3
import pandas as pd

# --- 1. ACCESS CONTROL ---
if 'user' not in st.session_state or st.session_state.get('role') != 'Restaurant':
    st.set_page_config(page_title="Access Denied", layout="centered")
    st.error("🚫 Access Denied. Please authenticate as a Restaurant Partner.")
    if st.button("Go to Login Portal"):
        st.switch_page("pages/Registration.py")
    st.stop()

# --- 2. GLOBAL PAGE CONFIG & SIDEBAR HIDE ---
st.set_page_config(page_title=f"NourishBridge | {st.session_state['user']}", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
        .stApp { background-color: #F9F8F3; }
        
        /* Unified Top Navigation */
        .nav-bar {
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 20px; background: white; border-bottom: 1px solid #EEE;
            margin: -60px -50px 30px -50px;
        }

        .metric-card { 
            background: white; padding: 25px; border-radius: 12px; 
            border: 1px solid #EAE9E4; text-align: left;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .metric-val { font-size: 32px; font-weight: 700; color: #1B3C33; margin: 0; }
        .metric-label { font-size: 14px; color: #666 !important; font-weight: 600; }
        .icon-bg { background-color: #E8F2EE; padding: 8px; border-radius: 8px; display: inline-block; margin-bottom: 5px; }
        
        .listing-card {
            background-color: white; padding: 25px; border-radius: 15px;
            border: 1px solid #F0EFEA; margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        }
        
        div.stButton > button {
            background-color: #2E5A48 !important; color: white !important;
            border-radius: 8px !important; font-weight: 600 !important;
            border: none !important;
        }
        div.stButton > button:hover { background-color: #D4A017 !important; }
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
        <div style='font-size: 22px; font-weight: 700; color: #1B3C33;'>🌱 NourishBridge </div>
        <div style='font-size: 14px; color: #666;'> <b>{st.session_state['user']}</b></div>
    </div>
""", unsafe_allow_html=True)

nav_col1, nav_col2 = st.columns([5, 1])
with nav_col2:
    if st.button("🚪 Logout", key="res_logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# --- 5. DYNAMIC MODALS ---
@st.dialog("Post Surplus Food")
def post_food_modal():
    food_type = st.selectbox("Food Type", ["Cooked Meals", "Baked Goods", "Fruits & Veg", "Packaged Food"])
    description = st.text_area("Description", placeholder="Describe the food items...")
    col_q, col_u = st.columns(2)
    with col_q: qty = st.number_input("Quantity", min_value=1, value=50)
    with col_u: unit = st.selectbox("Unit", ["Portions", "Packets", "Kgs"])
    deadline = st.text_input("Pickup Deadline", placeholder="e.g., 08:30 PM")
    
    if st.button("Confirm & Post Listing", use_container_width=True):
        run_cmd("INSERT INTO food (restaurant, type, quantity, status, location) VALUES (?, ?, ?, ?, ?)",
                (st.session_state['user'], f"{food_type}: {description}", qty, "available", st.session_state['location']))
        st.toast("Listing published to network!")
        st.rerun()

@st.dialog("Manage Requests")
def show_requests(food_id):
    food_data = run_query("SELECT quantity, type FROM food WHERE id=?", (food_id,))
    current_stock = int(food_data.iloc[0]['quantity'])
    
    st.write(f"📊 **Inventory Level:** {current_stock} portions remaining")
    st.divider()

    reqs = run_query("SELECT id, home, requested_qty FROM requests WHERE food_id=? AND status='Pending Approval'", (food_id,))
    
    if reqs.empty:
        st.info("No active requests for this listing.")
    else:
        for _, r in reqs.iterrows():
            requested_qty = int(r['requested_qty'])
            with st.container():
                c1, c2 = st.columns([2, 1])
                c1.write(f"🏠 **{r['home']}**")
                c1.caption(f"Requesting: {requested_qty} portions")
                
                if c2.button("Approve ✅", key=f"ap_{r['id']}"):
                    if current_stock <= 0:
                        st.error("Inventory exhausted.")
                    else:
                        actual_allocated = min(requested_qty, current_stock)
                        is_partial = actual_allocated < requested_qty
                        
                        run_cmd("UPDATE requests SET status='Pending Pickup', requested_qty=? WHERE id=?", (actual_allocated, r['id']))
                        run_cmd("UPDATE food SET quantity = quantity - ? WHERE id = ?", (actual_allocated, food_id))
                        
                        if (current_stock - actual_allocated) <= 0:
                            run_cmd("UPDATE food SET status = 'fully claimed' WHERE id = ?", (food_id,))
                        
                        if is_partial:
                            st.toast(f"⚠️ Partial: Allocated {actual_allocated} portions to {r['home']}.", icon="⚠️")
                        else:
                            st.toast(f"✅ Full allocation confirmed for {r['home']}.", icon="🍱")
                        st.rerun()
                
                if c2.button("Reject ❌", key=f"rej_{r['id']}"):
                    run_cmd("UPDATE requests SET status='Rejected' WHERE id=?", (r['id'],))
                    st.rerun()

# --- 6. DASHBOARD CONTENT ---
col_title, col_action = st.columns([3, 1])
with col_title:
    st.title("Restaurant Command Center")
    st.write(f"📍 Location: {st.session_state['location']}")

with col_action:
    st.write("##")
    if st.button("➕ Post New Surplus", use_container_width=True):
        post_food_modal()

# Metrics
df_food = run_query("SELECT * FROM food WHERE restaurant=?", (st.session_state['user'],))
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f"<div class='metric-card'><div class='icon-bg'>📦</div><p class='metric-val'>{len(df_food)}</p><p class='metric-label'>Total Listings</p></div>", unsafe_allow_html=True)
with m2: st.markdown(f"<div class='metric-card'><div class='icon-bg'>🕒</div><p class='metric-val'>{len(df_food[df_food['status']=='available'])}</p><p class='metric-label'>Available Listings</p></div>", unsafe_allow_html=True)

pending_pickup = run_query("""
    SELECT count(*) as count FROM requests r 
    JOIN food f ON r.food_id = f.id 
    WHERE f.restaurant=? AND r.status='Pending Pickup'
""", (st.session_state['user'],)).iloc[0]['count']
with m3: st.markdown(f"<div class='metric-card'><div class='icon-bg'>⚠️</div><p class='metric-val'>{pending_pickup}</p><p class='metric-label'>Active Pickups</p></div>", unsafe_allow_html=True)

st.divider()
st.subheader("Your Active Listings")

if df_food.empty:
    st.info("No active listings found. Use the button above to post your first surplus meal.")
else:
    for _, row in df_food.iterrows():
        f_id = int(row['id'])
        count_req = run_query("SELECT count(*) as count FROM requests WHERE food_id=? AND status='Pending Approval'", (f_id,)).iloc[0]['count']
        
        st.markdown(f"""
            <div class='listing-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <div>
                        <span style='font-size: 20px; font-weight: 700; color:#1B3C33;'>{row['type'].split(':')[0]}</span>
                        <span style='margin-left:10px; background: #E8F2EE; color: #2E5A48; padding: 4px 12px; border-radius: 20px; font-size: 12px;'>{row['status'].upper()}</span>
                        <p style='color: #666; margin-top: 5px;'>{row['type'].split(':')[-1] if ':' in row['type'] else ''}</p>
                        <p style='font-size:14px; font-weight: 600;'>📦 Stock: {row['quantity']} portions</p>
                    </div>
                    <div style='text-align: right;'>
                        <p style='color: #888; font-size:12px;'>Pending Requests</p>
                        <p style='font-size: 24px; font-weight: 700; color: #D4A017;'>{count_req}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        act1, act2, _ = st.columns([1, 1, 2])
        with act1:
            if st.button(f"Manage Requests ({count_req})", key=f"v_{f_id}", disabled=(count_req == 0)):
                show_requests(f_id)
        with act2:
            if st.button("🗑️ Remove Listing", key=f"c_{f_id}"):
                run_cmd("DELETE FROM food WHERE id=?", (f_id,))
                run_cmd("DELETE FROM requests WHERE food_id=?", (f_id,))
                st.rerun()