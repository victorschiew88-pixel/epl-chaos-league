import streamlit as st
from supabase import create_client, Client

# --- DB CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="EPL Chaos League", page_icon="⚽")

# --- THE NUCLEAR UI CLEANUP ---
hide_st_style = """
            <style>
            /* 1. THE BIG WIPE: Hide the entire right-side header block by position */
            header[data-testid="stHeader"] > div:nth-child(2) {
                display: none !important;
                visibility: hidden !important;
                width: 0 !important;
            }

            /* 2. SPECIFIC TARGETS: Catch anything the first rule missed */
            [data-testid="stHeaderActionElements"], 
            .stElementToolbar, 
            [data-testid="stStatusWidget"],
            button[title="Manage app"],
            #MainMenu {
                display: none !important;
            }

            /* 3. THE BOX POSITION: Physically shift the card down */
            .stMainBlockContainer {
                max-width: 600px !important;
                margin-top: 10vh !important; /* Drops the box down 10% of the screen */
                padding-top: 0px !important; /* Removes the gap inside the top of the box */
                background-color: rgba(0, 0, 0, 0.45) !important;
                border-radius: 25px;
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            /* 4. THE BACKGROUND */
            .stApp {
                background: url("https://i.ibb.co/gLvhXvTV/stadium-PM.png");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }

            /* 5. SIDEBAR TOGGLE: Move it so it doesn't overlap the box */
            [data-testid="stSidebarCollapsedControl"] {
                background-color: #00FF85 !important;
                color: black !important;
                border-radius: 5px;
                position: fixed !important;
                top: 20px !important;
                left: 20px !important;
                z-index: 999999 !important;
            }

            /* 6. Text Clarity */
            .stMarkdown, p, h1, h2, h3, label {
                color: white !important;
                text-shadow: 2px 2px 4px rgba(0,0,0,1);
            }
            
            /* Final polish: hide the tiny line at the very top */
            [data-testid="stDecoration"] {
                display: none !important;
            }
            footer {visibility: hidden;}
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
            existing_pred = user_preds.get(str(f['id']))

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
                        "match_id": str(f['id']),
                        "home_pred": h_val,
                        "away_pred": a_val
                    }, on_conflict="player_nickname, match_id").execute()
                    st.balloons()
                    st.toast("Prediction saved!")
                    st.rerun()
                except Exception as e: # This must line up with 'try'
                    st.error(f"DATABASE SAYS: {e}") # This must be indented inside 'except'                
                            
    # --- TAB 2: THE TABLE ---
    with tabs[1]:
        st.header("🏆 The League Table")
        
        # Pull all relevant columns
        leaderboard_res = supabase.table("players").select("nickname, favorite_team, w, d, l, points").order("points", desc=True).execute()
        
        if leaderboard_res.data:
            # Top 3 Metrics
            top_cols = st.columns(3)
            for i, player in enumerate(leaderboard_res.data[:3]):
                with top_cols[i]:
                    medal = ["🥇", "🥈", "🥉"][i]
                    st.metric(label=f"{medal} {player['nickname']}", value=f"{player['points']} pts")

            # Create the DataFrame
            df = pd.DataFrame(leaderboard_res.data)
            
            # Calculate Matches Played (MP)
            df['mp'] = df['w'] + df['d'] + df['l']
            
            # Reorder and Rename columns to match your second image
            df = df[['nickname', 'favorite_team', 'mp', 'w', 'd', 'l', 'points']]
            df.columns = ["Manager", "Club", "MP", "W", "D", "L", "Pts"]
            
            # Display the table
            st.dataframe(df, use_container_width=True, hide_index=True)
                    
    # --- TAB 3: CHAIRMAN'S OFFICE ---
    if len(tabs) > 2:
        with tabs[2]:
            st.title("💼 Chairman's Office")
            st.write("Welcome back, Boss. Use this area to manage the league.")
            # Only Victor can see these tools
            if user['nickname'] == 'victor':
                with st.expander("⚖️ Admin: Final Result Processing", expanded=True):
                    st.subheader("Confirm Match Results")

                    # Dropdown to pick the match
                    match_options = [f"{f['home_team']} vs {f['away_team']}" for f in fixtures]
                    match_to_score = st.selectbox("Which match just finished?", options=match_options)

                    # Input the ACTUAL final scores
                    col1, col2 = st.columns(2)
                    with col1:
                        h_real = st.number_input("Real Home Goals", min_value=0, step=1, key="real_h")
                    with col2:
                        a_real = st.number_input("Real Away Goals", min_value=0, step=1, key="real_a")

                    if st.button("🚀 PROCESS RESULTS & AWARD POINTS", use_container_width=True, key="admin_process_btn"):
                        # Find the specific fixture ID
                        selected_f = next(f for f in fixtures if f"{f['home_team']} vs {f['away_team']}" == match_to_score)
                    
                        # Fetch all predictions for this match
                        preds = supabase.table("predictions").select("*").eq("match_id", str(selected_f['id'])).execute()

                        if preds.data:
                            for p in preds.data:
                                # Calculate points using the REAL scores provided above
                                pts = calculate_points(p['home_pred'], p['away_pred'], h_real, a_real)

                                # Determine which column (w, d, l) to increment
                                stat_to_update = "l" 
                                if pts == 3:
                                    stat_to_update = "w"
                                elif pts == 1:
                                    stat_to_update = "d"

                                # Update the player's record
                                curr_res = supabase.table("players").select("points, w, d, l").eq("nickname", p['player_nickname']).execute()
                                if curr_res.data:
                                    curr = curr_res.data[0]
                                    supabase.table("players").update({
                                        "points": curr['points'] + pts,
                                        stat_to_update: curr.get(stat_to_update, 0) + 1
                                    }).eq("nickname", p['player_nickname']).execute()

                            st.success(f"Scores processed for {match_to_score}! Result: {h_real}-{a_real}")
                            st.balloons()
                        else:
                            st.warning("No predictions were found for this match.")
            else:
                st.warning("Chairman access only. Please return to the Changing Room.")
