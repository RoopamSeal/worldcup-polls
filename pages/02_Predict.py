"""
Predict page - Make predictions on matches.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Predict", layout="wide")

# Session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# Header
st.markdown("""
<h1 style="text-align: center;">🎯 MAKE YOUR PREDICTIONS</h1>
<p style="text-align: center; color: #e53238; font-size: 1rem;">
    Choose the winner before the match starts and earn points!
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Auth check
if st.session_state.user_id is None:
    st.warning("⚠️ You are not logged in.")
    st.info("👈 Please go to **Home** to log in.")
    st.stop()

# Info
st.info("⏰ **All times in IST (Indian Standard Time)**")

# Import
try:
    from src.storage import get_storage
    from src.predictions import PredictionManager
    from src.config import Config
    
    config = Config()
    storage = get_storage()
    pred_manager = PredictionManager(config, storage)
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

try:
    # Get matches
    matches = storage.get_all_matches()
    
    if not matches:
        st.warning("📭 No matches in database")
        st.stop()
    
    # Filter active
    active = [m for m in matches if m.get('status', '').lower() == 'scheduled']
    
    if not active:
        st.info("⏰ No upcoming matches")
        st.stop()
    
    # Get dates
    dates = sorted(set(m['match_date'] for m in active))
    
    # Date selector
    selected_date = st.selectbox(
        "Select Date",
        dates,
        format_func=lambda d: pd.to_datetime(d).strftime('%B %d, %Y')
    )
    
    # Get matches for date
    day_matches = [m for m in active if m['match_date'] == selected_date]
    
    if not day_matches:
        st.info("No matches on this date")
        st.stop()
    
    # Display count
    st.subheader(f"📋 {len(day_matches)} Matches on {pd.to_datetime(selected_date).strftime('%B %d, %Y')}")
    
    st.markdown("")
    
    # Display matches
    for match in day_matches:
        # Check prediction
        pred = storage.get_prediction(match['match_id'], st.session_state.user_id)
        
        # Colors
        if pred:
            bg = "#e8f5e9"
            border = "#4caf50"
            status = "✅ PREDICTED"
            status_color = "#4caf50"
        else:
            bg = "#e2e8f0"
            border = "#ffb81c"
            status = "🎯 OPEN"
            status_color = "#ffb81c"
        
        # Card
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.write(f"**{match['team_1']}**")
        
        with col2:
            st.write("**vs**")
        
        with col3:
            st.write(f"**{match['team_2']}**")
        
        st.caption(f"📅 {match['match_date']} | 🕐 {match['kickoff_time']} IST | {match['stage']}")
        
        # Prediction
        if pred:
            st.success(f"✅ Your prediction: **{pred['predicted_winner']}**")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(
                    f"🎯 {match['team_1']}",
                    key=f"p_{match['match_id']}_1",
                    use_container_width=True
                ):
                    success, msg, _ = pred_manager.make_prediction(
                        st.session_state.user_id,
                        match['match_id'],
                        match['team_1']
                    )
                    
                    if success:
                        st.success("✅ Prediction saved!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")
            
            with col2:
                if st.button(
                    "🤝 DRAW",
                    key=f"p_{match['match_id']}_draw",
                    use_container_width=True
                ):
                    success, msg, _ = pred_manager.make_prediction(
                        st.session_state.user_id,
                        match['match_id'],
                        'draw'
                    )
                    
                    if success:
                        st.success("✅ Prediction saved!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")
            
            with col3:
                if st.button(
                    f"🎯 {match['team_2']}",
                    key=f"p_{match['match_id']}_2",
                    use_container_width=True
                ):
                    success, msg, _ = pred_manager.make_prediction(
                        st.session_state.user_id,
                        match['match_id'],
                        match['team_2']
                    )
                    
                    if success:
                        st.success("✅ Prediction saved!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")
        
        st.markdown("---")

except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    st.error(f"Error: {str(e)}")
