"""
My Predictions page - View prediction history with FIFA 2026 design
Debugged and improved version using new architecture
"""
import sys
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import Config
from src.core.exceptions import StorageError
from src.services.prediction_service import PredictionService
from src.repository.match_repo import MatchRepository
from src.ui.components import Components
from src.ui.theme import Theme

# ============ LOGGING ============
logger = logging.getLogger(__name__)

# ============ PAGE CONFIG ============
st.set_page_config(page_title="My Predictions - World Cup 2026", layout="wide")

# ============ THEME ============
st.markdown(Theme.get_css(), unsafe_allow_html=True)

# ============ ADDITIONAL CSS FIXES ============
st.markdown("""
<style>
    /* Fix metric card text visibility */
    .metric-card {
        background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
        padding: 1.2rem;
        border-radius: 0.8rem;
        border: 2px solid #ffb81c;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 0.5rem;
    }
    
    .metric-card p {
        color: #1a472a !important;
        margin: 0 !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
    }
    
    .metric-card h3 {
        color: #e53238 !important;
        border: none !important;
        margin: 0.5rem 0 !important;
        font-size: 2rem !important;
    }
    
    /* Prediction card styling */
    .prediction-card {
        border-radius: 0.8rem;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .prediction-card:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ============ INITIALIZATION ============
try:
    config = Config()
    config.ensure_directories()
    prediction_service = PredictionService(config)
    match_repo = MatchRepository(config)
except Exception as e:
    st.error(f"Failed to initialize services: {e}")
    logger.error(f"Initialization error: {e}")
    st.stop()

# ============ TITLE ============
st.markdown("""
<h1 style="text-align: center;">📊 MY PREDICTIONS</h1>
<p style="text-align: center; color: #e53238; font-size: 1rem;">
    Track your prediction history and performance metrics
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ============ AUTHENTICATION CHECK ============
if st.session_state.user_id is None:
    st.info("👈 Please log in from the Home page to view your predictions")
    st.stop()

# ============ DATA LOADING WITH ERROR HANDLING ============
try:
    # Get user's predictions with error handling
    predictions = prediction_service.get_user_predictions(st.session_state.user_id)
    
    if not predictions:
        st.info("🎯 You haven't made any predictions yet. Go to the Predict page to get started!")
        st.stop()
    
    # Convert to DataFrame with error handling
    predictions_df = pd.DataFrame(predictions)
    
    # Validate DataFrame
    required_columns = ['match_id', 'predicted_winner', 'prediction_timestamp']
    if not all(col in predictions_df.columns for col in required_columns):
        st.error("Invalid prediction data structure")
        logger.error(f"Missing columns in predictions: {predictions_df.columns.tolist()}")
        st.stop()
    
    # Get match information with error handling
    try:
        all_matches = match_repo.get_all()
        if not all_matches:
            st.error("No matches available in database")
            st.stop()
        
        matches_df = pd.DataFrame(all_matches)
    except Exception as e:
        st.error(f"Error loading matches: {e}")
        logger.error(f"Match loading error: {e}")
        st.stop()
    
    # Merge data safely
    try:
        predictions_df = predictions_df.merge(
            matches_df[['match_id', 'team_1', 'team_2', 'match_date', 'kickoff_time', 'stage']],
            on='match_id',
            how='left'
        )
    except Exception as e:
        st.error(f"Error merging prediction and match data: {e}")
        logger.error(f"Merge error: {e}")
        st.stop()
    
    # Validate merged data
    if predictions_df.isnull().any(axis=1).any():
        st.warning("⚠️ Some predictions have incomplete match information")
        predictions_df = predictions_df.dropna(subset=['team_1', 'team_2'])
    
    # Sort by date descending
    try:
        predictions_df = predictions_df.sort_values('prediction_timestamp', ascending=False)
    except Exception as e:
        logger.warning(f"Error sorting predictions: {e}")

except Exception as e:
    st.error(f"Error loading predictions: {e}")
    logger.error(f"Prediction loading error: {e}")
    st.stop()

# ============ STATISTICS SECTION ============
st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>📈 Your Performance</h2>", 
            unsafe_allow_html=True)

try:
    total_preds = len(predictions_df)
    
    # Count correct predictions safely
    correct = 0
    for _, pred in predictions_df.iterrows():
        try:
            result = match_repo.get_result(pred['match_id'])
            if result and result.get('actual_winner') == pred['predicted_winner']:
                correct += 1
        except Exception as e:
            logger.warning(f"Error checking result for match {pred['match_id']}: {e}")
            continue
    
    # Calculate accuracy
    accuracy = (correct / total_preds * 100) if total_preds > 0 else 0
    
    # Get total points
    try:
        points = prediction_service.prediction_repo.get_user_total_points(st.session_state.user_id)
    except Exception as e:
        logger.error(f"Error getting user points: {e}")
        points = 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p>🎯 Total Predictions</p>
            <h3>{total_preds}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p>✅ Correct Predictions</p>
            <h3>{correct}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p>📊 Accuracy Rate</p>
            <h3>{accuracy:.1f}%</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <p>⭐ Total Points</p>
            <h3>{points}</h3>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error calculating statistics: {e}")
    logger.error(f"Statistics error: {e}")
    st.stop()

st.markdown("---")

# ============ FILTERS AND SORTING ============
st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>🔍 Filter & Sort</h2>", 
            unsafe_allow_html=True)

col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    status_filter = st.multiselect(
        "Filter by Status",
        ["All", "Pending", "Correct", "Incorrect"],
        default=["All"],
        help="Filter predictions by result status"
    )

with col_filter2:
    stage_filter = st.multiselect(
        "Filter by Stage",
        ["All"] + predictions_df['stage'].unique().tolist(),
        default=["All"],
        help="Filter by tournament stage"
    )

with col_filter3:
    sort_option = st.selectbox(
        "Sort By",
        ["Most Recent", "Oldest First", "Stage"],
        help="Choose sorting order"
    )

# Apply filters
filtered_df = predictions_df.copy()

# Status filter
if "All" not in status_filter and status_filter:
    status_matches = []
    for status in status_filter:
        mask = []
        for _, pred in filtered_df.iterrows():
            try:
                result = match_repo.get_result(pred['match_id'])
                if status == "Pending" and result is None:
                    mask.append(True)
                elif status == "Correct" and result and result['actual_winner'] == pred['predicted_winner']:
                    mask.append(True)
                elif status == "Incorrect" and result and result['actual_winner'] != pred['predicted_winner']:
                    mask.append(True)
                else:
                    mask.append(False)
            except:
                mask.append(False)
        status_matches.extend(mask)
    
    filtered_df = filtered_df[status_matches]

# Stage filter
if "All" not in stage_filter and stage_filter:
    filtered_df = filtered_df[filtered_df['stage'].isin(stage_filter)]

# Apply sorting
if sort_option == "Oldest First":
    filtered_df = filtered_df.sort_values('prediction_timestamp', ascending=True)
elif sort_option == "Stage":
    stage_order = {stage: i for i, stage in enumerate(["Group", "Round of 16", "Quarterfinals", "Semifinals", "Final"])}
    filtered_df['stage_order'] = filtered_df['stage'].map(stage_order)
    filtered_df = filtered_df.sort_values('stage_order', ascending=False).drop('stage_order', axis=1)

st.markdown("---")

# ============ PREDICTION HISTORY ============
st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>📋 Prediction History</h2>", 
            unsafe_allow_html=True)

if filtered_df.empty:
    st.info("No predictions match your filter criteria")
else:
    # Pagination
    items_per_page = 10
    total_items = len(filtered_df)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # Page selector
    col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
    
    with col_page1:
        page_num = st.number_input(
            "Page",
            min_value=1,
            max_value=max(1, total_pages),
            value=1,
            help=f"Showing {total_items} predictions"
        )
    
    with col_page2:
        st.caption(f"Showing {(page_num-1)*items_per_page + 1} - {min(page_num*items_per_page, total_items)} of {total_items}")
    
    # Get page data
    start_idx = (page_num - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_data = filtered_df.iloc[start_idx:end_idx]
    
    st.markdown("")
    
    # Display predictions
    for idx, (_, pred) in enumerate(page_data.iterrows(), 1):
        try:
            # Get match result
            result = match_repo.get_result(pred['match_id'])
            
            # Parse datetime with proper timezone handling
            try:
                match_datetime = pd.to_datetime(f"{pred['match_date']} {pred['kickoff_time']}")
                # Convert UTC to IST (UTC+5:30)
                match_datetime_ist = match_datetime + timedelta(hours=5, minutes=30)
                formatted_date = match_datetime_ist.strftime('%B %d, %Y')
                formatted_time = match_datetime_ist.strftime('%H:%M IST')
            except Exception as e:
                logger.warning(f"Error parsing datetime: {e}")
                formatted_date = pred['match_date']
                formatted_time = pred['kickoff_time']
            
            # Determine status
            if result:
                is_correct = result['actual_winner'] == pred['predicted_winner']
                if is_correct:
                    status_icon = "✅"
                    status_text = "CORRECT"
                    status_color = "#4caf50"
                    bg_color = "#e8f5e9"
                    actual_result = result['actual_winner']
                else:
                    status_icon = "❌"
                    status_text = "INCORRECT"
                    status_color = "#e53238"
                    bg_color = "#ffebee"
                    actual_result = result['actual_winner']
                
                # Calculate points
                points_earned = prediction_service.calculate_points(
                    pred['predicted_winner'],
                    result['actual_winner']
                )
                
                result_info = f"<strong>Result:</strong><br><span style='color: #666;'>{actual_result}</span>"
                points_info = f'<span style="background: #ffb81c; color: #1a472a; padding: 0.4rem 0.6rem; border-radius: 0.3rem; font-weight: 600; display: block;">+{points_earned} PTS</span>'
            else:
                status_icon = "⏳"
                status_text = "PENDING"
                status_color = "#2196f3"
                bg_color = "#e3f2fd"
                actual_result = "-"
                result_info = "<br>—"
                points_info = ""
            
            # Sanitize team names to prevent HTML injection
            team_1 = str(pred['team_1']).replace('<', '&lt;').replace('>', '&gt;')
            team_2 = str(pred['team_2']).replace('<', '&lt;').replace('>', '&gt;')
            predicted = str(pred['predicted_winner']).replace('<', '&lt;').replace('>', '&gt;')
            stage = str(pred['stage']).replace('<', '&lt;').replace('>', '&gt;')
            
            # Render prediction card
            st.markdown(f"""
            <div class="prediction-card" style="background: {bg_color}; padding: 1.2rem; border-radius: 0.8rem; border-left: 5px solid {status_color}; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="display: grid; grid-template-columns: 2fr 1fr 2fr 1fr 1fr; gap: 1rem; align-items: center;">
                    <div>
                        <h4 style="color: #1a472a; margin: 0; font-size: 1rem; font-weight: 700;">{team_1}</h4>
                    </div>
                    <div style="text-align: center;">
                        <span style="background: #ffb81c; color: #1a472a; padding: 0.3rem 0.6rem; border-radius: 0.3rem; font-weight: 600; font-size: 0.8rem;">vs</span>
                    </div>
                    <div>
                        <h4 style="color: #1a472a; margin: 0; font-size: 1rem; font-weight: 700;">{team_2}</h4>
                    </div>
                    <div style="text-align: center;">
                        <p style="color: #666; margin: 0; font-size: 0.85rem;">
                            <strong>Your Pick:</strong><br>
                            <span style="color: #1a472a; font-weight: 700;">{predicted}</span>
                            {result_info}
                        </p>
                    </div>
                    <div style="text-align: center;">
                        <span style="background: {status_color}; color: white; padding: 0.5rem 0.8rem; border-radius: 0.4rem; font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 0.5rem;">
                            {status_icon} {status_text}
                        </span>
                        {points_info}
                    </div>
                </div>
                <div style="margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid rgba(0,0,0,0.1);">
                    <small style="color: #999;">
                        📅 {formatted_date} at {formatted_time} • 
                        <span style="background: #e53238; color: white; padding: 0.2rem 0.4rem; border-radius: 0.2rem; font-size: 0.75rem; font-weight: 600;">
                            {stage}
                        </span>
                    </small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        except Exception as e:
            st.warning(f"Error displaying prediction {idx}: {e}")
            logger.error(f"Prediction display error for {pred.get('match_id')}: {e}")
            continue
    
    # Pagination controls
    if total_pages > 1:
        st.markdown("---")
        col_prev, col_dots, col_next = st.columns([1, 1, 1])
        
        with col_prev:
            if page_num > 1:
                if st.button("← Previous", use_container_width=True):
                    st.rerun()
        
        with col_dots:
            st.caption(f"Page {page_num} of {total_pages}")
        
        with col_next:
            if page_num < total_pages:
                if st.button("Next →", use_container_width=True):
                    st.rerun()
