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
    # Exact Score: 3 Points
    if home_pred == home_actual and away_pred == away_actual:
        return 3
    # Correct Result (Win/Loss/Draw): 1 Point
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
    st.title("🏆 THE EPL CHAOS LEAGUE")
    tab1, tab2 = st.tabs(["🏟️ Login", "📝 Register"])
    
    with tab2:
        reg_nick = st.text_input("Choose Nickname")
        # --- TEAMS LIST (Top 3 Tiers 2025/26) ---
        premier_league = [
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton & Hove Albion", 
            "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Leeds United", 
            "Liverpool", "Man City", "Man Utd", "Newcastle United", "Nottingham Forest", 
            "Sunderland", "Spurs", "West Ham", "Wolves"
        ]
        
        championship = [
            "Birmingham City", "Blackburn Rovers", "Bristol City", "Charlton Athletic", 
            "Coventry City", "Derby County", "Hull City", "Ipswich Town", "Leicester City", 
            "Middlesbrough", "Millwall", "Norwich City", "Oxford United", "Portsmouth", 
            "Preston North End", "QPR", "Sheffield United", "Sheffield Wednesday", 
            "Southampton", "Stoke City", "Swansea City", "Watford", "West Brom", "Wrexham"
        ]
        
        league_one = [
            "AFC Wimbledon", "Barnsley", "Blackpool", "Bolton Wanderers", "Bradford City", 
            "Burton Albion", "Cardiff City", "Doncaster Rovers", "Exeter City", 
            "Huddersfield Town", "Leyton Orient", "Lincoln City", "Luton Town", 
            "Mansfield Town", "Northampton Town", "Peterborough United", "Plymouth Argyle", 
            "Port Vale", "Reading", "Rotherham United", "Stevenage", "Stockport County", 
            "Wigan Athletic", "Wycombe Wanderers"
        ]

        # Combine all for the dropdown
        all_teams = sorted(premier_league + championship + league_one) + ["Other"]
        
        reg_team = st.selectbox("Select Your Team", all_teams)
        reg_pin = st.text_input("4-Digit PIN", type="password", max_chars=4)
        if st.button("SIGN CONTRACT"):
            # 1. Check if nickname is empty
            if not reg_nick:
                st.warning("⚠️ Please choose a nickname first!")
            # 2. Check if PIN is valid
            elif not (len(reg_pin) == 4 and reg_pin.isdigit()):
                st.warning("⚠️ Your PIN must be exactly 4 numbers.")
            # 3. Everything is good, try to register
            else:
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

    # --- TAB NAVIGATION ---
    # Only show 'Chairman's Office' if the nickname is yours! 
    # REPLACE 'YourNickname' with your actual nickname in the quotes below.
    if user['nickname'] == "victor":
        tabs = st.tabs(["👟 Changing Room", "🏆 Table", "💼 Chairman's Office"])
    else:
        tabs = st.tabs(["👟 Changing Room", "🏆 Table"])

    # --- TAB 1: CHANGING ROOM (The Predictions) ---
    with tabs[0]:
        st.markdown("<h1 style='text-align: center; color: #00ff87;'>🦁 THE CHANGING ROOM</h1>", unsafe_allow_html=True)
        
        from datetime import datetime
        import pytz
        import pandas as pd
                
        uk_tz = pytz.timezone("Europe/London")
        now = datetime.now(uk_tz)
        # Fetch fixtures from Supabase
        fixtures_res = supabase.table("fixtures").select("*").order("deadline").execute()
        fixtures = fixtures_res.data if fixtures_res.data else []
            
        for f in fixtures:
                        is_locked = now > pd.to_datetime(f['deadline']).tz_convert("Europe/London")
                        with st.container(border=True):
                            status_emoji = "🔒" if is_locked else "📅"
                            st.write(f"{status_emoji} **{f['deadline']}**")
                            c1, c2, c3 = st.columns([2, 1, 2])
                            h_val = c1.number_input(f"{f['home_team']}", min_value=0, step=1, key=f"{f['id']}_h", disabled=is_locked)
                            c2.markdown("<h3 style='text-align: center; padding-top: 20px;'>vs</h3>", unsafe_allow_html=True)
                            a_val = c3.number_input(f"{f['away_team']}", min_value=0, step=1, key=f"{f['id']}_a", disabled=is_locked)
                            
                            btn_label = "LOCKED" if is_locked else f"Lock {f['home_team']} vs {f['away_team']}"
                            if st.button(btn_label, key=f"btn_{f['id']}", use_container_width=True, disabled=is_locked):
                                supabase.table("predictions").upsert({
                                    "player_nickname": user['nickname'],
                                    "match_id": f['id'],
                                    "home_pred": h_val,
                                    "away_pred": a_val
                                }, on_conflict=["player_nickname", "match_id"]).execute()
                                st.balloons()
                                st.toast(f"Prediction saved!")

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
            
            with st.expander("🛠️ Fixture Management (Coming Soon)"):
                st.write("This is where we'll add the API automation later today.")
            
            with st.expander("📝 Enter Final Results"):
                st.info("Select a match and enter the score to award points.")
                
                # 1. This picks the match from our list
                match_to_score = st.selectbox("Select Match", [f['home_team'] + " vs " + f['away_team'] for f in fixtures])
                
                c1, c2 = st.columns(2)
                h_score = c1.number_input("Home Score", min_value=0, step=1, key="admin_h")
                a_score = c2.number_input("Away Score", min_value=0, step=1, key="admin_a")
                
                if st.button("🏆 PROCESS RESULTS & AWARD POINTS", use_container_width=True):
                    # 2. Identify which fixture we are scoring
                    selected_f = next(f for f in fixtures if f['home'] + " vs " + f['away'] == match_to_score)
                    
                    # 3. Get everyone's predictions for this specific match
                    preds = supabase.table("predictions").select("*").eq("match_id", selected_f['id']).execute()
                    
                    for p in preds.data:
                        # 4. Use the math engine at the top of your file to get the pts
                        pts = calculate_points(p['home_pred'], p['away_pred'], h_score, a_score)
                        
                        # 5. Fetch their current total and add the new points
                        current_player = supabase.table("players").select("points").eq("nickname", p['player_nickname']).execute()
                        new_total = current_player.data[0]['points'] + pts
                        
                        # 6. Save the new total back to the database
                        supabase.table("players").update({"points": new_total}).eq("nickname", p['player_nickname']).execute()
                    
                    st.success(f"Scores processed! Points awarded for {match_to_score}.")
                    st.balloons()
