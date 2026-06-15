import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="FIFA World Cup Predictor", layout="wide")

# ==========================================
# 2. DATA LAKE SIMULATION (Medallion Architecture)
# ==========================================
# In production, these point to your Unity Catalog / S3 / ADLS paths
SILVER_DIR = "data_lake/silver"
GOLD_DIR = "data_lake/gold"

def init_datalake():
    """Initializes dummy Data Lake tables if they don't exist."""
    os.makedirs(f"{SILVER_DIR}/user_master", exist_ok=True)
    os.makedirs(f"{SILVER_DIR}/match_master", exist_ok=True)
    os.makedirs(f"{SILVER_DIR}/prediction_fact", exist_ok=True)
    os.makedirs(f"{SILVER_DIR}/match_result", exist_ok=True)
    os.makedirs(f"{GOLD_DIR}/leaderboard", exist_ok=True)
    
    # Mock Match Master Data
    match_file = f"{SILVER_DIR}/match_master/data.parquet"
    if not os.path.exists(match_file):
        pd.DataFrame({
            "match_id": ["M1", "M2", "M3"],
            "team_1": ["Brazil", "Spain", "Argentina"],
            "team_2": ["Germany", "France", "Netherlands"],
            "stage": ["Group", "Group", "Quarter-Final"],
            "match_date": [datetime.today().date()] * 3,
            "kickoff_time": ["18:00", "20:00", "22:00"],
            "status": ["Upcoming", "Upcoming", "Finished"]
        }).to_parquet(match_file, index=False)
        
    # Mock Prediction Fact
    pred_file = f"{SILVER_DIR}/prediction_fact/data.parquet"
    if not os.path.exists(pred_file):
        pd.DataFrame(columns=[
            "prediction_id", "user_id", "match_id", "predicted_winner", "prediction_timestamp"
        ]).to_parquet(pred_file, index=False)

    # Mock Match Results
    result_file = f"{SILVER_DIR}/match_result/data.parquet"
    if not os.path.exists(result_file):
        pd.DataFrame({
            "match_id": ["M3"],
            "actual_winner": ["Argentina"],
            "result_timestamp": [datetime.now()]
        }).to_parquet(result_file, index=False)

    # Mock Gold Leaderboard
    lb_file = f"{GOLD_DIR}/leaderboard/data.parquet"
    if not os.path.exists(lb_file):
        pd.DataFrame({
            "user_id": ["Soumya", "Rahul", "Amit"],
            "total_predictions": [10, 9, 8],
            "correct_predictions": [6, 5, 4],
            "accuracy_percentage": [60.0, 55.5, 50.0],
            "total_points": [32, 29, 28],
            "rank": [1, 2, 3]
        }).to_parquet(lb_file, index=False)

init_datalake()

# --- Helper Functions (Swap with PySpark/SQL in Prod) ---
def read_table(layer, table_name):
    path = f"data_lake/{layer}/{table_name}/data.parquet"
    return pd.read_parquet(path) if os.path.exists(path) else pd.DataFrame()

def write_prediction(user_id, match_id, predicted_winner):
    path = f"{SILVER_DIR}/prediction_fact/data.parquet"
    df = pd.read_parquet(path)
    
    # Upsert logic (overwrite if user already predicted this match)
    df = df[~((df['user_id'] == user_id) & (df['match_id'] == match_id))]
    
    new_pred = pd.DataFrame([{
        "prediction_id": str(uuid.uuid4()),
        "user_id": user_id,
        "match_id": match_id,
        "predicted_winner": predicted_winner,
        "prediction_timestamp": datetime.now()
    }])
    
    df = pd.concat([df, new_pred], ignore_index=True)
    df.to_parquet(path, index=False)

# ==========================================
# 3. UI DASHBOARD & NAVIGATION
# ==========================================
st.sidebar.title("⚽ Navigation")
# Hardcoded user context for simulation
current_user = st.sidebar.selectbox("Log in as:", ["Soumya", "Rahul", "Amit", "NewUser"])
menu = st.sidebar.radio("Go to", ["Home (Today's Matches)", "My Predictions", "Leaderboard"])

# ------------------------------------------
# SCREEN 1: Home (Today's Matches)
# ------------------------------------------
if menu == "Home (Today's Matches)":
    st.title("Today's Matches")
    
    matches = read_table("silver", "match_master")
    predictions = read_table("silver", "prediction_fact")
    
    today = datetime.today().date()
    today_matches = matches[(matches['match_date'] == today) & (matches['status'] == 'Upcoming')]
    
    if today_matches.empty:
        st.info("No upcoming matches today.")
    else:
        for _, match in today_matches.iterrows():
            st.divider()
            st.subheader(f"{match['team_1']} vs {match['team_2']}")
            st.caption(f"Kickoff: {match['kickoff_time']} | {match['stage']}")
            
            # Check if user already predicted
            user_preds = predictions[(predictions['user_id'] == current_user) & (predictions['match_id'] == match['match_id'])]
            
            if not user_preds.empty:
                st.success(f"You predicted: **{user_preds.iloc[0]['predicted_winner']}**")
            else:
                # Prediction Form
                with st.form(key=f"form_{match['match_id']}"):
                    choice = st.radio(
                        "Predict Winner:", 
                        [match['team_1'], match['team_2'], "Draw"],
                        key=f"radio_{match['match_id']}"
                    )
                    submit = st.form_submit_button("Submit Prediction", type="primary")
                    
                    if submit:
                        write_prediction(current_user, match['match_id'], choice)
                        st.rerun()

# ------------------------------------------
# SCREEN 2: My Predictions
# ------------------------------------------
elif menu == "My Predictions":
    st.title("My Predictions")
    
    preds = read_table("silver", "prediction_fact")
    matches = read_table("silver", "match_master")
    results = read_table("silver", "match_result")
    
    # Filter for current user
    my_preds = preds[preds['user_id'] == current_user]
    
    if my_preds.empty:
        st.info("You haven't made any predictions yet.")
    else:
        # Join predictions with match details and actual results
        df = my_preds.merge(matches, on='match_id', how='left')
        df = df.merge(results, on='match_id', how='left')
        
        for _, row in df.iterrows():
            match_title = f"{row['team_1']} vs {row['team_2']}"
            pred = row['predicted_winner']
            actual = row['actual_winner']
            
            if pd.isna(actual):
                st.markdown(f"⏳ **{match_title}** → {pred} (Awaiting Result)")
            elif pred == actual:
                st.markdown(f"✅ **{match_title}** → {pred} (Correct)")
            else:
                st.markdown(f"❌ **{match_title}** → {pred} (Incorrect - Winner: {actual})")

# ------------------------------------------
# SCREEN 3: Leaderboard
# ------------------------------------------
elif menu == "Leaderboard":
    st.title("🏆 Leaderboard")
    
    # Read from Gold Layer
    lb = read_table("gold", "leaderboard")
    
    if lb.empty:
        st.info("Leaderboard is currently empty.")
    else:
        # Sort by Rank just in case
        lb = lb.sort_values(by='rank')
        
        st.dataframe(
            lb[['rank', 'user_id', 'total_points', 'accuracy_percentage']],
            column_config={
                "rank": "Rank",
                "user_id": "User",
                "total_points": "Points",
                "accuracy_percentage": st.column_config.NumberColumn("Accuracy", format="%.1f%%")
            },
            hide_index=True,
            use_container_width=True
        )
        st.caption("Leaderboard relies on the Points Calculation Job (Gold Layer updates).")
