import streamlit as st
from supabase import create_client, Client

# --- DB CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="EPL Chaos League", page_icon="⚽")

# --- HIDE STREAMLIT BRANDING ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- SCORING ENGINE ---
def calculate_points(home_pred, away_pred, home_actual, away_actual):
    # EXACT SCORE: 3 POINTS
    if home_pred == home_actual and away_pred == away_actual:
        return 3
    
    # CORRECT RESULT (Win/Loss/Draw): 1 POINT
    pred_diff = home_pred - away_pred
    actual_diff = home_actual - away_actual
    
    if (pred_diff > 0 and actual_diff > 0) or (pred_diff < 0 and actual_diff < 0) or (pred_diff == 0 and actual_diff == 0):
        return 1
    
    # Wrong Result: 0 Points
    return 0

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
    st.title("⚽ THE EPL CHAOS LEAGUE")
    tabL, tabR = st.tabs(["🔐 Login", "📝 Register"])

    with tabR:
        reg_nick = st.text_input("Choose Nickname")
        # TEAMS LIST
        teams = [
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton & Hove Albion",
            "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Leeds United",
            "Liverpool", "Man City", "Man Utd", "Newcastle United", "Nottingham Forest",
            "Sunderland", "Spurs", "West Ham", "Wolves"
        ]
        
        reg_team = st.selectbox("Select Your Team", all_teams if 'all_teams' in locals() else sorted(teams + ["Other"]))
        reg_pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        
        if st.button("SIGN CONTRACT"):
            if not reg_nick:
                st.warning("⚠️ Please choose a nickname first!")
            elif not (len(reg_pin) == 4 and reg_pin.isdigit()):
                st.warning("⚠️ Your PIN must be exactly 4 numbers.")
            else:
                if register(reg_nick, reg_pin, reg_team):
                    st.success("Signed! Now go to the Login tab.")
                else:
                    st.error("Nickname taken or system error!")

    with tabL:
        log_nick = st.text_input("Nickname")
        log_pin = st.text_input("PIN", type="password")
        if st.button("ENTER LOCKER ROOM"):
            if login(log_nick, log_pin):
                st.rerun()
            else:
                st.error("Invalid Nickname or PIN.")

# --- MAIN APP ---
else:
    user = st.session_state.user

    # --- SIDEBAR (Layout & Info) ---
    with st.sidebar:
        st.title(f"👋 {user['nickname']}")
        st.write(f"**Supporting:** {user['favorite_team']}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
        st.divider()
        st.info("Tip: 3 pts for exact score, 1 pt for correct result!")

    # --- TAB NAVIGATION ---
    if user['nickname'] == "victor":
        tabs = st.tabs(["⚽ Changing Room", "🏆 Table", "💼 Chairman's Office"])
    else:
        tabs = st.tabs(["⚽ Changing Room", "🏆 Table"])

    # --- TAB 1: CHANGING ROOM ---
    with tabs[0]:
        st.markdown("<h1 style='text-align: center; color: #00ff87;'>⚽ THE CHANGING ROOM</h1>", unsafe_allow_html=True)

        from datetime import datetime
        import pytz
        import pandas as pd

        uk_tz = pytz.timezone("Europe/London")
        now = datetime.now(uk_tz)

        # 1. Fetch fixtures
        fixtures_res = supabase.table("fixtures").select("*").order("deadline").execute()
        fixtures = fixtures_res.data if fixtures_res.data else []

        # 2. Fetch user's existing predictions to check status
        pred_res = supabase.table("predictions").select("*").eq("player_nickname", user['nickname']).execute()
        user_preds = {p['match_id']: p for p in pred_res.data} if pred_res.data else {}

        for f in fixtures:
            is_locked = now > pd.to_datetime(f['deadline']).tz_convert("Europe/London")
            existing_pred = user_preds.get(f['id'])

            with st.container(border=True):
                status_emoji = "🔒" if is_locked else "🗓️"
                clean_deadline = pd.to_datetime(f['deadline']).tz_convert("Europe/London").strftime("%a, %d %b - %H:%M")
                st.write(f"{status_emoji} **Deadline:** {clean_deadline}")

                c1, c2, c3 = st.columns([2, 1, 2])

                # Memory Logic: Show saved scores if they exist
                h_def = int(existing_pred['home_pred']) if existing_pred else 0
                a_def = int(existing_pred['away_pred']) if existing_pred else 0

                h_val = c1.number_input(f"{f['home_team']}", min_value=0, step=1, value=h_def, key=f"{f['id']}_h", disabled=is_locked)
                c2.markdown("<h3 style='text-align: center; padding-top: 20px;'>vs</h3>", unsafe_allow_html=True)
                a_val = c3.number_input(f"{f['away_team']}", min_value=0, step=1, value=a_def, key=f"{f['id']}_a", disabled=is_locked)

                # Dynamic Labels
                if is_locked:
                    btn_label = "🔒 LOCKED"
                elif existing_pred:
                    btn_label = f"📝 Edit {f['home_team']} vs {f['away_team']}"
                else:
                    btn_label = f"⚽ Lock {f['home_team']} vs {f['away_team']}"

                if st.button(btn_label, key=f"btn_{f['id']}", use_container_width=True, disabled=is_locked):
                    try:
                        res = supabase.table("predictions").upsert({
                            "player_nickname": user['nickname'],
                            "match_id": f['id'],
                            "home_pred": h_val,
                            "away_pred": a_val
                        }, on_conflict=["player_nickname", "match_id"]).execute()
                        st.balloons()
                        st.toast("Prediction saved!")
                        st.rerun() 
                    except Exception as e:
                        st.error(f"DATABASE SAYS: {e}")
                                
    # --- TAB 2: THE TABLE ---
    with tabs[1]:
        st.header("🏆 The League Table")
        leaderboard_res = supabase.table("players").select("nickname, favorite_team, points").order("points", desc=True).execute()
        if leaderboard_res.data:
            top_cols = st.columns(3)
            for i, player in enumerate(leaderboard_res.data[:3]):
                with top_cols[i]:
                    medal = ["🥇", "🥈", "🥉"][i]
                    st.metric(label=f"{medal} {player['nickname']}", value=f"{player['points']} pts")

            df = pd.DataFrame(leaderboard_res.data)
            df.columns = ["Manager", "Club", "Points"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 3: CHAIRMAN'S OFFICE ---
    if len(tabs) > 2:
        with tabs[2]:
            st.title("💼 Chairman's Office")
            st.write("Welcome back, Boss. Use this area to manage the league.")

            with st.expander("🏗️ Fixture Management (Coming Soon)"):
                st.write("This is where we'll add the API automation later today.")

            with st.expander("🎰 Enter Final Results"):
                st.info("Select a match and enter the score to award points.")

                match_to_score = st.selectbox("Select Match", [f['home_team'] + " vs " + f['away_team'] for f in fixtures])

                c1, c2 = st.columns(2)
                h_score = c1.number_input("Home Score", min_value=0, step=1, key="admin_h")
                a_score = c2.number_input("Away Score", min_value=0, step=1, key="admin_a")

                if st.button("🚀 PROCESS RESULTS & AWARD POINTS", use_container_width=True):
                    # FIX: Corrected column names to home_team and away_team
                    selected_f = next(f for f in fixtures if f['home_team'] + " vs " + f['away_team'] == match_to_score)

                    preds = supabase.table("predictions").select("*").eq("match_id", selected_f['id']).execute()

                    for p in preds.data:
                        pts = calculate_points(p['home_pred'], p['away_pred'], h_score, a_score)

                        current_player = supabase.table("players").select("points").eq("nickname", p['player_nickname']).execute()
                        new_total = current_player.data[0]['points'] + pts

                        supabase.table("players").update({"points": new_total}).eq("nickname", p['player_nickname']).execute()

                    st.success(f"Scores processed! Points awarded for {match_to_score}.")
                    st.balloons()
