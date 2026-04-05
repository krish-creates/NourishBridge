import streamlit as st
import sqlite3
import pandas as pd

# --- 1. GLOBAL PAGE CONFIG ---
st.set_page_config(
    page_title="NourishBridge | Login Portal", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. HIDE SIDEBAR & CUSTOM CSS ---
st.markdown("""
    <style>
    /* Hide Sidebar Completely */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    .stApp { background-color: #F9F8F3; }
    
    /* Navigation Bar */
    .nav-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 0; border-bottom: 1px solid #EEE; margin-bottom: 30px;
    }

    .header-banner {
        background: linear-gradient(90deg, #1B3C33 0%, #2E5A48 100%);
        color: white; padding: 40px; text-align: center;
        border-radius: 15px; margin-bottom: 40px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .hub-card {
        background-color: white; border-radius: 12px; padding: 30px 20px;
        text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: 0.3s ease; height: 100%; border: 1px solid #EEE;
    }
    .hub-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
    .hub-icon { font-size: 55px; margin-bottom: 15px; display: block; }
    .hub-title { font-weight: 700; font-size: 22px; margin-bottom: 10px; }
    .hub-desc { color: #666; font-size: 14px; margin-bottom: 20px; min-height: 45px; }

    /* Button Overrides */
    div.stButton > button {
        background-color: #2E5A48 !important; color: white !important;
        border-radius: 8px !important; font-weight: 600 !important;
        border: none !important; width: 100% !important; height: 3em !important;
    }
    div.stButton > button:hover { background-color: #D4A017 !important; }
    
    .spotlight-box {
        background: white; border: 1px solid #E0E0E0;
        border-left: 5px solid #800000; padding: 20px; border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE FOR LOGIN FLOW ---
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None

# --- 4. TOP NAVIGATION ---
st.markdown("""
    <div class='nav-bar'>
        <div style='font-size: 20px; font-weight: 700; color: #1B3C33;'>🌱 NourishBridge</div>
        <div style='font-size: 14px; color: #666;'>Official Access Gateway</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. HEADER BANNER ---
st.markdown(f"""
    <div class='header-banner'>
        <h1 style='color:white !important; margin:0; font-size: 36px;'>{"Choose Your Role" if not st.session_state.selected_role else "Secure Portal Access"}</h1>
        <p style='color:#E8F2EE; margin-top:10px; font-size: 16px; opacity: 0.9;'>Select your role to manage your contributions and requests.</p>
    </div>
""", unsafe_allow_html=True)

# --- 6. VIEW LOGIC ---

if st.session_state.selected_role:
    # Back button as a clean link
    if st.button("⬅️ Change Role"):
        st.session_state.selected_role = None
        st.rerun()
        
    st.markdown(f"<h2 style='text-align:center; margin-top:20px;'>🔑 {st.session_state.selected_role} Login</h2>", unsafe_allow_html=True)
    
    col_l, col_mid, col_r = st.columns([1, 1.5, 1])
    with col_mid:
        # --- ADMIN ACCESS ---
        if st.session_state.selected_role == "Admin":
            with st.form("admin_gate"):
                st.info("🛡️ System Administrator Verification Required")
                admin_key = st.text_input("Master Access Key", type="password", placeholder="Enter secret key...")
                submit_admin = st.form_submit_button("Verify & Enter Dashboard")

                if submit_admin:
                    if admin_key == "adminkrish": 
                        st.session_state['role'] = 'Admin'
                        st.session_state['user'] = 'System Admin'
                        st.switch_page("pages/1_Admin.py")
                    else:
                        st.error("❌ Invalid Access Key.")

        # --- STANDARD USER ACCESS ---
        else:
            with st.form("login_form"):
                u_name = st.text_input("Username")
                u_pass = st.text_input("Password", type="password")
                submit = st.form_submit_button(f"Sign In as {st.session_state.selected_role}")

                if submit:
                    with sqlite3.connect('food_hero.db') as conn:
                        cur = conn.cursor()
                        cur.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", 
                                   (u_name, u_pass, st.session_state.selected_role))
                        user = cur.fetchone()
                        
                    if user:
                        # Check approval status
                        if user[6] == 1:
                            st.session_state['user'] = user[4]
                            st.session_state['role'] = user[3]
                            st.session_state['location'] = user[5]
                            # Store internal ID for payout processing
                            st.session_state['user_id_from_db'] = user[1] 
                            
                            routes = {
                                "Restaurant": "pages/2_Restaurant.py", 
                                "Homes": "pages/3_Homes.py", 
                                "Delivery Hero": "pages/4_Delivery_Hero.py"
                            }
                            st.switch_page(routes[user[3]])
                        else:
                            st.warning("⏳ Compliance Notice: Account pending Admin approval.")
                    else:
                        st.error(f"❌ Authentication Failed: Invalid credentials for {st.session_state.selected_role}.")

else:
    # ROLE SELECTION VIEW
    roles = [
        {"name": "Restaurant", "icon": "🍴", "color": "#2E5A48", "desc": "ISO-certified kitchens posting surplus meals."},
        {"name": "Homes", "icon": "🏠", "color": "#D4A017", "desc": "Verified shelters requesting food allocation."},
        {"name": "Delivery Hero", "icon": "🚴", "color": "#2E5A48", "desc": "NGO-funded logistics and distribution."},
        {"name": "Admin", "icon": "🛡️", "color": "#D4A017", "desc": "Platform audit and user verification."}
    ]
    
    col_roles = st.columns(4)
    for i, role in enumerate(roles):
        with col_roles[i]:
            st.markdown(f"""
                <div class='hub-card' style='border-top: 6px solid {role['color']};'>
                    <span class='hub-icon'>{role['icon']}</span>
                    <div class='hub-title' style='color: {role['color']};'>{role['name']}</div>
                    <p class='hub-desc'>{role['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Enter as {role['name']}", key=f"btn_{role['name']}"):
                st.session_state.selected_role = role['name']
                st.rerun()

# --- 7. BOTTOM FOOTER SECTION ---
st.write("##")
st.divider()

c_left, c_right = st.columns([1.5, 1])
with c_left:
    st.markdown("<h3 style='color:#800000; font-size: 20px;'>⚡ Live Updates</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div class='spotlight-box'>
            <p style='margin:5px 0; font-size:14px;'>📢 <a href='#'>New: ISO 22000 Mandatory for all Restaurant Partners</a></p>
            <hr style='margin:10px 0; opacity: 0.3;'>
            <p style='margin:5px 0; font-size:14px;'>📢 <a href='#'>NGO Funding: Delivery Hero payouts increased to ₹50/drop</a></p>
            <hr style='margin:10px 0; opacity: 0.3;'>
            <p style='margin:5px 0; font-size:14px;'>📢 <a href='#'>System Maintenance: Sunday 2:00 AM - 4:00 AM</a></p>
        </div>
    """, unsafe_allow_html=True)

with c_right:
    st.markdown("### Access Anywhere")
    ca, cb = st.columns(2)
    with ca: st.image("https://upload.wikimedia.org/wikipedia/commons/7/78/Google_Play_Store_badge_EN.svg")
    with cb: st.image("https://upload.wikimedia.org/wikipedia/commons/3/3c/Download_on_the_App_Store_Badge.svg")

st.write("---")
# Fixed Back Button
if st.button("⬅️ Return to Landing Page", key="back_to_app"):
    st.switch_page("app.py")