"""
My Predictions page - Show user's prediction history.
"""

import streamlit as st
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="My Predictions", layout="wide")

# Session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Header
st.markdown("""
<h1 style="text-align: center;">📊 MY PREDICTIONS</h1>
""", unsafe_allow_html=True)

st.markdown("---")

# Auth check
if st.session_state.user_id is None:
    st.warning("⚠️ Not logged in. Go to Home to log in.")
    st.stop()

# Import
try:
    from src.storage import get_storage
    storage = get_storage()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

try:
    # Get predictions
    predictions = storage.get_user_predictions(st.session_state.user_id)
    
    if not predictions:
        st.info("📭 No predictions yet. Go to Predict page!")
        st.stop()
    
    # Get stats
    stats = storage.get_user_stats(st.session_state.user_id)
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Total", stats['total_predictions'])
    with col2:
        st.metric("✅ Correct", stats['correct_predictions'])
    with col3:
        st.metric("📊 Accuracy", f"{stats['accuracy']:.1f}%")
    with col4:
        st.metric("⭐ Points", stats['total_points'])
    
    st.markdown("---")
    
    # Predictions
    st.subheader("Prediction History")
    
    for pred in predictions:
        # Get match info
        match = storage.get_match(pred['match_id'])
        result = storage.get_result(pred['match_id'])
        
        if not match:
            continue
        
        # Determine status
        if result:
            is_correct = result['actual_winner'] == pred['predicted_winner']
            if is_correct:
                status = "✅ CORRECT"
                status_color = "#4caf50"
                bg = "#e8f5e9"
            else:
                status = "❌ INCORRECT"
                status_color = "#e53238"
                bg = "#ffebee"
        else:
            status = "⏳ PENDING"
            status_color = "#2196f3"
            bg = "#e3f2fd"
        
        # Display
        st.markdown(f"""
        <div style="background: {bg}; padding: 1rem; border-radius: 0.8rem;
                    border-left: 4px solid {status_color}; margin-bottom: 1rem;">
            <div style="display: grid; grid-template-columns: 2fr 1fr 2fr 1fr 1fr; gap: 1rem;">
                <div><h4 style="color: #1a472a; margin: 0;">{match['team_1']}</h4></div>
                <div style="text-align: center;">vs</div>
                <div><h4 style="color: #1a472a; margin: 0;">{match['team_2']}</h4></div>
                <div style="text-align: center;">
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">
                        Your: {pred['predicted_winner']}<br>
                        {f"Result: {result['actual_winner']}" if result else "Pending"}
                    </p>
                </div>
                <div style="text-align: center;">
                    <span style="background: {status_color}; color: white; padding: 0.5rem;
                               border-radius: 0.4rem; font-weight: 600; font-size: 0.85rem;">
                        {status}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    st.error(f"Error: {str(e)}")
