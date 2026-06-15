import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="FIFA World Cup 2026 Poll",
    page_icon="⚽",
    layout="wide"  # Needed for side-by-side layout (Polls vs Leaderboard)
)

# File Paths based on image_91f1ec.png
FIXTURE_FILE = Path("data/FIFA2026_schedule_fixtures.csv")
VOTES_FILE = Path("data/votes.csv")

# Ensure directories exist
FIXTURE_FILE.parent.mkdir(exist_ok=True)

# Automatically initialize votes.csv with the exact requested columns if missing/empty
if not VOTES_FILE.exists() or VOTES_FILE.stat().st_size == 0:
    pd.DataFrame(
        columns=[
            "vote_id",
            "match_number",
            "username",
            "prediction",
            "timestamp",
            "score"
        ]
    ).to_csv(VOTES_FILE, index=False)

# ==========================================
# 2. DATA LOADERS & MUTATORS
# ==========================================
@st.cache_data(ttl=60)  # Caches for 1 minute to stay resource-friendly but responsive
def load_fixtures():
    try:
        df = pd.read_csv(FIXTURE_FILE)
        # Parse dates uniformly (adjust format string if your file uses a different delimiter/order)
        df["date_dt"] = pd.to_datetime(df["date_dt"], errors="coerce")
        return df
    except FileNotFoundError:
        st.error(f"⚠️ Fixtures file missing at `{FIXTURE_FILE}`. Please upload it to your data directory.")
        st.stop()

def load_votes():
    try:
        return pd.read_csv(VOTES_FILE)
    except Exception:
        # Fallback if file gets corrupted
        return pd.DataFrame(columns=["vote_id", "match_number", "username", "prediction", "timestamp", "score"])

def save_vote(match_number, username, prediction):
    votes = load_votes()
    
    # Create the record matching your requested database schema
    new_record = {
        "vote_id": str(uuid.uuid4()),
        "match_number": str(match_number),
        "username": username.strip(),
        "prediction": prediction,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": 0  # Initialized to 0. Updated to 10 points when match outcome is resolved.
    }
    
    # Append and save
    votes = pd.concat([votes, pd.DataFrame([new_record])], ignore_index=True)
    votes.to_csv(VOTES_FILE, index=False)

# ==========================================
# 3. INTERACTIVE USER INTERFACE
# ==========================================

# Divide layout into two columns: Left for Polls, Right for Leaderboard
left_col, right_col = st.columns([2, 1], gap="large")

# --- LEFT COLUMN: MATCH POLLS ---
with left_col:
    st.title("🏆 FIFA World Cup 2026 Poll")
    
    username = st.text_input("Enter your Username to vote:", placeholder="e.g., Roopam")
    
    if not username:
        st.info("👋 Please enter your username above to view today's matches and place your predictions!")
    else:
        fixtures = load_fixtures()
        
        # Dynamically fetch current date to filter matches
        today = pd.Timestamp.today().normalize()
        today_games = fixtures[fixtures["date_dt"].dt.normalize() == today]
        
        if len(today_games) == 0:
            st.write("---")
            st.info("📅 No matches scheduled for today. Check back tomorrow for more action!")
        else:
            votes = load_votes()
            
            for _, game in today_games.iterrows():
                match_id = str(game["match_number"])
                team1 = game["team 1"]
                team2 = game["team 2"]
                
                st.write("---")
                st.subheader(f"🏟️ Match {match_id}: {team1} vs {team2}")
                
                # Check if this user has already voted for this specific match
                user_match_vote = votes[
                    (votes["username"].str.lower() == username.strip().lower()) & 
                    (votes["match_number"].astype(str) == match_id)
                ]
                
                if len(user_match_vote) == 0:
                    # Render voting poll options
                    choice = st.radio(
                        "Who will win?",
                        options=[team1, team2, "Draw"],
                        key=f"poll_{match_id}",
                        label_visibility="collapsed"  # Clean aesthetic mimicking the layout wireframe
                    )
                    
                    if st.button("Submit Prediction", key=f"btn_{match_id}", type="primary"):
                        save_vote(match_id, username, choice)
                        st.success("⚽ Prediction locked in successfully!")
                        st.balloons()
                        st.rerun()
                else:
                    voted_choice = user_match_vote.iloc[0]["prediction"]
                    st.info(f"✅ Your locked prediction: **{voted_choice}**")
                
                # Show live visual breakdown of how the group is voting on this match
                match_predictions = votes[votes["match_number"].astype(str) == match_id]
                if not match_predictions.empty:
                    with st.expander("📊 View Group Voting Trends", expanded=False):
                        chart_data = match_predictions["prediction"].value_counts()
                        st.bar_chart(chart_data)

# --- RIGHT COLUMN: DYNAMIC LEADERBOARD ---
with right_col:
    st.header("🏅 Leaderboard")
    st.write("Top 5 Predictors")
    
    all_votes = load_votes()
    
    if all_votes.empty:
        st.info("The tournament leaderboard is empty. Submit a prediction to appear here!")
    else:
        # Dynamically calculate totals grouped by username
        leaderboard_df = (
            all_votes.groupby("username")["score"]
            .sum()
            .reset_index()
            .sort_values(by="score", ascending=False)
            .head(5)
        )
        
        # Format index nicely for the top 5 ranking display
        leaderboard_df.index = range(1, len(leaderboard_df) + 1)
        
        # Display as a polished, styled ranking table
        st.dataframe(
            leaderboard_df,
            column_config={
                "username": st.column_config.TextColumn("User Name"),
                "score": st.column_config.NumberColumn("Total Score", format="%d PTS 🏆")
            },
            use_container_width=True
        )
