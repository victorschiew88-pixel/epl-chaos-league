import streamlit as st

st.set_page_config(page_title="EPL Chaos League", page_icon="⚽")

# --- REAL FIXTURES: GAMEWEEK 34 ---
fixtures = [
    {"home": "Sunderland", "away": "Nott'm Forest", "time": "Friday 20:00"},
    {"home": "Fulham", "away": "Aston Villa", "time": "Saturday 12:30"},
    {"home": "West Ham", "away": "Everton", "time": "Saturday 15:00"},
    {"home": "Wolves", "away": "Spurs", "time": "Saturday 15:00"},
    {"home": "Liverpool", "away": "Crystal Palace", "time": "Saturday 15:00"},
    {"home": "Arsenal", "away": "Newcastle", "time": "Saturday 17:30"},
    {"home": "Man Utd", "away": "Brentford", "time": "Monday 20:00"}
]

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏆 THE EPL CHAOS LEAGUE")
    if st.button("ENTER LOCKER ROOM (DEMO MODE)"):
        st.session_state.logged_in = True
        st.rerun()
else:
    st.title("👟 Matchday Predictions")
    st.write("Gameweek 34 - Squeaky Bum Time!")
    
    for match in fixtures:
        with st.container(border=True):
            st.write(f"⏰ {match['time']}")
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1: st.subheader(match['home'])
            with col2: st.write("### vs")
            with col3: st.subheader(match['away'])
            
            c1, c2 = st.columns(2)
            h_score = c1.number_input(f"{match['home']} Score", min_value=0, step=1, key=f"{match['home']}_h")
            a_score = c2.number_input(f"{match['away']} Score", min_value=0, step=1, key=f"{match['away']}_a")
    
    if st.button("LOCK ALL PREDICTIONS"):
        st.balloons()
        st.success("All scores saved to the void! (Database coming next)")
