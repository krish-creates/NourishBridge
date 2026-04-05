import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. GLOBAL PAGE CONFIG & SIDEBAR HIDE ---
st.set_page_config(page_title="NourishBridge | Admin Audit", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
        .stApp { background-color: #F9F8F3 !important; }
        
        /* Top Navigation Styling */
        .nav-bar {
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 20px; background: white; border-bottom: 1px solid #EEE;
            margin: -60px -50px 30px -50px;
        }

        /* Metric Card Buttons */
        div.stButton > button {
            background-color: white !important;
            color: #1B3C33 !important;
            border: 1px solid #EAE9E4 !important;
            padding: 20px !important;
            border-radius: 12px !important;
            text-align: left !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
            transition: 0.3s !important;
            height: auto !important;
        }
        div.stButton > button:hover {
            border-color: #D4A017 !important;
            transform: translateY(-2px);
            background-color: #FDFCF9 !important;
        }
        
        .data-card {
            background: white; padding: 20px; border-radius: 12px;
            border: 1px solid #EEE; margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }
        .doc-badge {
            background: #E8F2EE; color: #2E5A48; padding: 4px 10px;
            border-radius: 5px; font-size: 12px; font-weight: 700;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. THE GATEKEEPER ---
if 'role' not in st.session_state or st.session_state['role'] != 'Admin':
    st.error("🛑 Unauthorized Access. Please authenticate via the Admin Portal.")
    if st.button("⬅️ Return to Hub"):
        st.session_state.clear()
        st.switch_page("pages/Registration.py")
    st.stop()

# --- 3. TOP NAVIGATION ---
st.markdown(f"""
    <div class='nav-bar'>
        <div style='font-size: 22px; font-weight: 700; color: #1B3C33;'>🛡️ Admin Audit Command</div>
        <div style='font-size: 14px; color: #666;'>System Status: <span style='color:green;'>● Online</span></div>
    </div>
""", unsafe_allow_html=True)

# Right-aligned Logout Button
col_header, col_logout = st.columns([5, 1])
with col_logout:
    if st.button("🚪 Logout", key="admin_logout"):
        st.session_state.clear()
        st.switch_page("app.py")

# --- 4. DATABASE HELPERS ---
def run_query(q, params=()):
    with sqlite3.connect('food_hero.db') as conn:
        return pd.read_sql_query(q, conn, params=params)

def run_cmd(q, params=()):
    with sqlite3.connect('food_hero.db') as conn:
        cur = conn.cursor()
        cur.execute(q, params)
        conn.commit()

# --- 5. INITIALIZE STATE ---
if 'admin_view' not in st.session_state:
    st.session_state.admin_view = "Verification"

# --- 6. DYNAMIC METRICS (VERIFIED ONLY) ---
all_users = run_query("SELECT role, is_approved FROM users")

# INTELLIGENT METRICS: Only count where is_approved == 1
rest_count = len(all_users[(all_users['role'] == 'Restaurant') & (all_users['is_approved'] == 1)])
home_count = len(all_users[(all_users['role'] == 'Homes') & (all_users['is_approved'] == 1)])
hero_count = len(all_users[(all_users['role'] == 'Delivery Hero') & (all_users['is_approved'] == 1)])
pending_count = len(all_users[all_users['is_approved'] == 0])

# --- 7. INTERACTIVE METRIC ROW ---
m1, m2, m3, m4 = st.columns(4)

with m1:
    if st.button(f"🍴 **{rest_count}**\nVerified Restaurants", use_container_width=True):
        st.session_state.admin_view = "Restaurant"
with m2:
    if st.button(f"🏠 **{home_count}**\nVerified Homes", use_container_width=True):
        st.session_state.admin_view = "Homes"
with m3:
    if st.button(f"🚴 **{hero_count}**\nVerified Heroes", use_container_width=True):
        st.session_state.admin_view = "Delivery Hero"
with m4:
    # Highlighting the Pending Queue in Red/Gold if count > 0
    btn_label = f"👤 **{pending_count}**\nPending Audit"
    if st.button(btn_label, use_container_width=True):
        st.session_state.admin_view = "Verification"

st.divider()

# --- 8. DYNAMIC CONTENT AREA ---

# VIEW 1: VERIFICATION QUEUE (THE AUDITOR)
if st.session_state.admin_view == "Verification":
    st.subheader("🔍 Compliance Audit Queue")
    pending = run_query("SELECT * FROM users WHERE is_approved = 0")
    
    if pending.empty:
        st.success("✅ All partners are verified.")
    else:
        for _, row in pending.iterrows():
            st.markdown(f"""
                <div class='data-card'>
                    <b>{row['display_name']}</b> ({row['role']})<br>
                    <small>📍 {row['location']}</small>
                    <span style='float:right;' class='doc-badge'>📄 {row['iso_doc']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # --- THE FIX: DOCUMENT PREVIEW ---
            with st.expander("👁️ View Uploaded Document"):
                try:
                    st.image(row['iso_doc'], use_container_width=True)
                except:
                    st.warning("File preview not available. Check project folder.")

            c1, c2, _ = st.columns([1, 1, 4])
            with c1:
                if st.button("Verify ✅", key=f"v_{row['id']}"):
                    run_cmd("UPDATE users SET is_approved=1 WHERE id=?", (row['id'],))
                    st.rerun()
            with c2:
                if st.button("Reject ❌", key=f"r_{row['id']}"):
                    run_cmd("DELETE FROM users WHERE id=?", (row['id'],))
                    st.rerun()
                st.write("---")

# VIEW 2: DIRECTORY VIEWS
elif st.session_state.admin_view in ["Restaurant", "Homes", "Delivery Hero"]:
    st.subheader(f"📋 Verified {st.session_state.admin_view} Directory")
    directory = run_query("SELECT display_name, location, earnings, iso_doc FROM users WHERE role=? AND is_approved=1", (st.session_state.admin_view,))
    
    if directory.empty:
        st.info(f"No verified {st.session_state.admin_view}s found in the active database.")
    else:
        for _, u in directory.iterrows():
            st.markdown(f"""
                <div class='data-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <b>{u['display_name']}</b>
                        <span style='color:green; font-weight:700;'>✓ ACTIVE</span>
                    </div>
                    <p style='font-size:14px; margin:5px 0;'>{u['location']}</p>
                    <div style='display:flex; gap:15px; margin-top:10px;'>
                        <small>🛡️ ISO Ref: {u['iso_doc']}</small>
                        {"<small>💰 NGO Wallet: ₹" + str(u['earnings']) + "</small>" if st.session_state.admin_view == "Delivery Hero" else ""}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 9. ANALYTICS TABS ---
st.write("##")
tab_stats, tab_live = st.tabs(["📊 Platform Analytics", "📡 Live Stream"])

with tab_stats:
    ca1, ca2 = st.columns(2)
    with ca1:
        st.write("### Network Composition")
        # Only analyze verified users for the chart
        active_users = all_users[all_users['is_approved'] == 1]
        if not active_users.empty:
            role_counts = active_users['role'].value_counts()
            fig, ax = plt.subplots(figsize=(6, 3))
            role_counts.plot(kind='pie', autopct='%1.1f%%', colors=['#1B3C33', '#2E7D5B', '#D4A017'], ax=ax)
            ax.set_ylabel('')
            fig.patch.set_facecolor('#F9F8F3')
            st.pyplot(fig)
    with ca2:
        st.write("### Resource Utilization")
        food_data = run_query("SELECT type FROM food")
        if not food_data.empty:
            types = food_data['type'].str.split(':').str[0].value_counts()
            st.bar_chart(types)

with tab_live:
    activity = run_query("""
        SELECT r.home, r.status, r.requested_qty, f.restaurant, f.type 
        FROM requests r 
        JOIN food f ON r.food_id = f.id 
        ORDER BY r.id DESC LIMIT 10
    """)
    if activity.empty:
        st.info("System Idle: No transactions currently in progress.")
    else:
        for _, act in activity.iterrows():
            st.markdown(f"""
                <div style='background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D5B; margin-bottom: 10px;'>
                    <b>{act['home']}</b> requested <b>{act['requested_qty']} units</b> from <b>{act['restaurant']}</b> 
                    <span style='float:right; font-size:10px; background:#EEE; padding:3px 8px; border-radius:10px;'>{act['status']}</span>
                </div>
            """, unsafe_allow_html=True)