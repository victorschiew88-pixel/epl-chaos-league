import streamlit as st
from supabase import create_client, Client

# --- DB CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="EPL Chaos League", page_icon="⚽")

# --- AUTH LOGIC ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login(nick, pin):
    res = supabase.table("players").select("*").eq("nickname", nick).eq("pin", pin).execute()
    if res.data:
        st.session_state.user = res.data[0]
        return True
    return False

def register(nick, pin, team):
    try:
        supabase.table("players").insert({"nickname": nick, "pin": pin, "favorite_team": team}).execute()
        return True
    except:
        return False

# --- UI: GATEWAY ---
if not st.session_state.user:
    st.title("🏆 THE EPL CHAOS LEAGUE")
    tab1, tab2 = st.tabs(["🏟️ Login", "📝 Register"])
    
    with tab2:
        reg_nick = st.text_input("Choose Nickname")
        reg_team = st.selectbox("Team", ["Arsenal", "Man City", "Liverpool", "Sunderland", "Newcastle", "Other"])
        reg_pin = st.text_input("4-Digit PIN", type="password")
        if st.button("SIGN CONTRACT"):
            if register(reg_nick, reg_pin, reg_team):
                st.success("Signed! Now go to the Login tab.")
            else:
                st.error("Nickname taken or system error!")

    with tab1:
        log_nick = st.text_input("Nickname")
        log_pin = st.text_input("PIN", type="password")
        if st.button("ENTER LOCKER ROOM"):
            if login(log_nick, log_pin):
                st.rerun()
            else:
                st.error("Invalid Nickname or PIN.")

# --- UI: MAIN APP ---
else:
    user = st.session_state.user

    # --- 1. SIDEBAR (Logout & Info) ---
    with st.sidebar:
        st.title(f"👋 {user['nickname']}")
        st.write(f"**Supporting:** {user['favorite_team']}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
        st.divider()
        st.info("Tip: 3 pts for exact score, 1 pt for correct result!")

    # --- 2. MAIN LOCKER ROOM ---
    st.markdown("""
        <h1 style='text-align: center; color: #00ff87; margin-bottom: 0px;'>
            🦁 THE EPL CHAOS LEAGUE
        </h1>
        <p style='text-align: center; color: #00f2ff; font-size: 24px; font-weight: bold; margin-top: 0px;'>
            👟 The Locker Room
        </p>
    """, unsafe_allow_html=True)
     
    fixtures = [
        {"id": "sun_not", "home": "Sunderland", "away": "Nott'm Forest", "time": "Fri 20:00"},
        {"id": "ful_avl", "home": "Fulham", "away": "Aston Villa", "time": "Sat 12:30"},
        {"id": "whu_eve", "home": "West Ham", "away": "Everton", "time": "Sat 15:00"},
        {"id": "ars_new", "home": "Arsenal", "away": "Newcastle", "time": "Sat 17:30"}
    ]

    for f in fixtures:
        with st.container(border=True):
            st.write(f"📅 **{f['time']}**")
            c1, c2, c3 = st.columns([2, 1, 2])
            
            h_val = c1.number_input(f"{f['home']}", min_value=0, step=1, key=f"{f['id']}_h")
            c2.markdown("<h3 style='text-align: center; padding-top: 20px;'>vs</h3>", unsafe_allow_html=True)
            a_val = c3.number_input(f"{f['away']}", min_value=0, step=1, key=f"{f['id']}_a")
            
            if st.button(f"Lock {f['home']} vs {f['away']}", key=f"btn_{f['id']}", use_container_width=True):
                supabase.table("predictions").insert({
                    "player_nickname": user['nickname'],
                    "match_id": f['id'],
                    "home_pred": h_val,
                    "away_pred": a_val
                }).execute()
                st.balloons()
                st.toast(f"Prediction saved for {f['home']}!")

    # --- 3. LEADERBOARD ---
    st.divider()
    st.header("🏆 The Global Standings")
    
    leaderboard_res = supabase.table("players").select("nickname, favorite_team, points").order("points", desc=True).execute()
    
    if leaderboard_res.data:
        # Top 3 Podium
        top_cols = st.columns(3)
        for i, player in enumerate(leaderboard_res.data[:3]):
            with top_cols[i]:
                medal = ["🥇", "🥈", "🥉"][i]
                st.metric(label=f"{medal} {player['nickname']}", value=f"{player['points']} pts")
        
        # Full Table
        import pandas as pd
        df = pd.DataFrame(leaderboard_res.data)
        df.columns = ["Manager", "Club", "Points"]
        st.dataframe(df, use_container_width=True, hide_index=True)
