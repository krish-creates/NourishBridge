import streamlit as st
import sqlite3
import os

# --- 1. GLOBAL PAGE CONFIG ---
st.set_page_config(page_title="NourishBridge | Signup", layout="centered", initial_sidebar_state="collapsed")

# --- 2. HIDE SIDEBAR & CUSTOM CSS ---
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    .stApp { background-color: #F9F8F3 !important; }
    
    /* Navigation Bar */
    .nav-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 0; border-bottom: 1px solid #EEE; margin-bottom: 30px;
    }
    
    /* Success Box */
    .success-box {
        background-color: #E8F2EE; padding: 25px; border-radius: 15px;
        border: 1px solid #2E5A48; text-align: center; color: #1B3C33;
    }
    
    /* Form Styling */
    div.stButton > button {
        background-color: #2E5A48 !important; color: white !important;
        border-radius: 8px !important; height: 3.5em !important; font-weight: 600 !important;
    }
    div.stButton > button:hover { background-color: #D4A017 !important; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE HELPER ---
def run_cmd(q, params=()):
    with sqlite3.connect('food_hero.db') as conn:
        cur = conn.cursor()
        cur.execute(q, params)
        conn.commit()

# --- TOP NAVIGATION ---
st.markdown("""
    <div class='nav-bar'>
        <div style='font-size: 20px; font-weight: 700; color: #1B3C33;'>🌱 NourishBridge</div>
        <div style='font-size: 14px; color: #666;'>Secure Registration Portal</div>
    </div>
""", unsafe_allow_html=True)

# --- SESSION STATE GATE ---
if 'signed_up' not in st.session_state:
    st.session_state.signed_up = False

# --- UI LOGIC ---
if st.session_state.signed_up:
    st.markdown("""
    <div class="success-box">
        <h3>🎉 Application Submitted</h3>
        <p>Your documentation has been saved and sent to our <b>Compliance Team</b>. <br>
        Administrative verification typically takes 24-48 hours.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("##")
    if st.button("⬅️ Return to Landing Page"):
        st.session_state.signed_up = False
        st.switch_page("app.py")
else:
    # Back Button
    if st.button("⬅️ Back", key="back_btn"):
        st.switch_page("app.py")

    st.title("📝 Partner Registration")
    st.write("Join our network of verified contributors.")
    
    role = st.selectbox("I am joining as a:", ["Select Role", "Restaurant", "Homes", "Delivery Hero"])

    if role != "Select Role":
        st.write("---")
        with st.form("signup_form", clear_on_submit=True):
            st.write(f"### Registering as: **{role}**")
            
            display_name = st.text_input("Official Entity Name", placeholder="e.g., Grand Plaza Hotel")
            username = st.text_input("Choose Login Username")
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                password = st.text_input("Create Secure Password", type="password")
            with col_p2:
                contact = st.text_input("Official Contact Number")
                
            location = st.text_area("Registered Address (Will be used for map routing)")

            # --- DYNAMIC COMPLIANCE FIELDS ---
            doc_file = None
            if role == "Restaurant":
                st.info("ℹ️ ISO 22000 or Food Safety Certification is required.")
                doc_file = st.file_uploader("Upload ISO/FSSAI Certificate", type=['jpg', 'png', 'jpeg'])

            elif role == "Homes":
                st.info("ℹ️ Welfare homes must provide a Government Registration Certificate.")
                doc_file = st.file_uploader("Upload Welfare Registration", type=['jpg', 'png', 'jpeg'])

            elif role == "Delivery Hero":
                st.info("ℹ️ Delivery partners must provide a valid Government ID.")
                doc_file = st.file_uploader("Upload Driver's License / National ID", type=['jpg', 'png', 'jpeg'])

            st.write("##")
            submitted = st.form_submit_button("Submit Application for Audit")

            if submitted:
                if not username or not password or not display_name or not location or doc_file is None:
                    st.error("⚠️ All fields and compliance documents are mandatory.")
                else:
                    try:
                        # --- FILE SAVING LOGIC ---
                        # This takes the file from the uploader and saves it to your project folder
                        file_name = doc_file.name
                        with open(file_name, "wb") as f:
                            f.write(doc_file.getbuffer())
                        
                        # --- DATABASE LOGIC ---
                        run_cmd("""
                            INSERT INTO users (username, password, role, display_name, location, is_approved, iso_doc) 
                            VALUES (?, ?, ?, ?, ?, 0, ?)
                        """, (username, password, role, display_name, location, file_name))
                        
                        st.balloons()
                        st.session_state.signed_up = True
                        st.rerun()

                    except sqlite3.IntegrityError:
                        st.error("❌ Username already registered. Please choose another.")
                    except Exception as e:
                        st.error(f"❌ System Error: {e}")

st.markdown("<p style='text-align:center; color:#888; font-size:12px; margin-top:50px;'>By submitting, you agree to NourishBridge safety protocols and auditing standards.</p>", unsafe_allow_html=True)