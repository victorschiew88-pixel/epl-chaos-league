import streamlit as st

# --- APP CONFIG ---
st.set_page_config(page_title="EPL Chaos League", page_icon="⚽", layout="centered")

# --- CUSTOM CSS FOR THE "BANTER" VIBE ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #262730; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE (The App's Memory) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LANDING PAGE: THE STADIUM GATES ---
if not st.session_state.logged_in:
    st.title("🏆 THE EPL CHAOS LEAGUE")
    st.subheader("Where Predictions Mean War.")
    
    tab1, tab2 = st.tabs(["🆕 New Signing (Register)", "🏟️ Match Day Login"])
    
    with tab1:
        st.write("First time? Sign your contract below.")
        new_nick = st.text_input("Nickname (The 'Hero' name)")
        new_team = st.selectbox("Favorite Team", ["Arsenal", "Liverpool", "Man City", "Spurs", "Everton", "Brighton", "Other"])
        new_pin = st.text_input("Choose a 4-Digit PIN", type="password", help="Don't forget this, or you'll be a Goldfish!")
        if st.button("SIGN CONTRACT"):
            if new_nick and new_pin:
                st.success(f"Welcome to the League, {new_nick}! Now go to the Login tab.")
            else:
                st.error("Fill in your details, rookie!")

    with tab2:
        st.write("Enter the Locker Room.")
        login_nick = st.text_input("Nickname")
        login_pin = st.text_input("Enter PIN", type="password")
        if st.button("ENTER LOCKER ROOM"):
            # For now, we'll let anyone in to test the UI
            st.session_state.logged_in = True
            st.rerun()

# --- THE MAIN APP (Once Logged In) ---
else:
    st.title("👟 The Locker Room")
    st.write(f"Welcome back! Your matches are waiting.")
    
    # DUMMY MATCH CARD
    st.info("NEXT MATCH: Sunday, 4:30 PM")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.image("https://logodownload.org/wp-content/uploads/2019/10/arsenal-logo-0.png", width=80)
        st.write("**Arsenal**")
    with col2:
        st.write("## VS")
    with col3:
        st.image("https://logodownload.org/wp-content/uploads/2019/10/liverpool-fc-logo.png", width=80)
        st.write("**Liverpool**")
        
    score_h = st.number_input("Home Score", min_value=0, step=1, key="h1")
    score_a = st.number_input("Away Score", min_value=0, step=1, key="a1")
    
    if st.button("LOCK IN PREDICTION"):
        st.balloons()
        st.success(f"Prediction Locked: {score_h} - {score_a}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
