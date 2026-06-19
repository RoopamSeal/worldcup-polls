"""
My Predictions page - View prediction history with timeline style
"""
import streamlit as st
import pandas as pd
from src.config import Config
from src.storage import Storage
from src.ui import inject_global_css, timeline_prediction, progress_bar

# Initialize
config = Config()
storage = Storage(config)
storage.initialize_data_layer()

inject_global_css()
st.set_page_config(page_title="My Predictions - World Cup 2026", layout="wide")

# Check authentication
if st.session_state.user_id is None:
    st.info("Please log in from the main page")
    st.stop()

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <div style="
        font-family: 'Montserrat', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #0057B8 0%, #00C896 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    ">📊 Your Predictions</div>
    <div style="
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.7);
    ">Timeline of your predictions and results.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

try:
    # Get user's predictions
    predictions = storage.get_user_predictions(st.session_state.user_id)
    
    if not predictions:
        st.info("You haven't made any predictions yet. Go to the Predict page to get started!")
        st.stop()
    
    predictions_df = pd.DataFrame(predictions)
    
    # Get match information
    all_matches = pd.DataFrame(storage.get_all_matches())
    
    # Merge data
    predictions_df = predictions_df.merge(
        all_matches[['match_id', 'team_1', 'team_2', 'match_date', 'kickoff_time', 'stage']],
        on='match_id',
        how='left'
    )
    
    # Sort by date descending
    predictions_df['match_datetime'] = pd.to_datetime(
        predictions_df['match_date'] + ' ' + predictions_df['kickoff_time']
    )
    predictions_df = predictions_df.sort_values('match_datetime', ascending=False)
    
    # Stats
    st.markdown('<h2>📈 Your Statistics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_predictions = len(predictions_df)
    
    correct = 0
    for _, pred in predictions_df.iterrows():
        result = storage.get_match_result(pred['match_id'])
        if result and result['actual_winner'] == pred['predicted_winner']:
            correct += 1
    
    accuracy = (correct / total_predictions * 100) if total_predictions > 0 else 0
    points = storage.get_user_total_points(st.session_state.user_id)
    
    with col1:
        st.metric("Total Predictions", total_predictions, label_visibility="collapsed")
    with col2:
        st.metric("Correct", correct, label_visibility="collapsed")
    with col3:
        st.metric("Accuracy", f"{accuracy:.1f}%", label_visibility="collapsed")
    with col4:
        st.metric("Points", points, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Progress bar
    st.markdown('<h3>Accuracy Progress</h3>', unsafe_allow_html=True)
    progress_bar(correct, total_predictions, f"You got {correct} out of {total_predictions} correct")
    
    st.markdown("---")
    
    # Timeline
    st.markdown('<h2>⏱️ Prediction Timeline</h2>', unsafe_allow_html=True)
    
    for _, pred in predictions_df.iterrows():
        result = storage.get_match_result(pred['match_id'])
        match_datetime = pd.to_datetime(f"{pred['match_date']} {pred['kickoff_time']}")
        
        points_earned = 0
        if result:
            if result['actual_winner'] == pred['predicted_winner']:
                if pred['predicted_winner'] == 'draw':
                    points_earned = config.POINTS_CORRECT_DRAW
                else:
                    points_earned = config.POINTS_CORRECT_WINNER
        
        timeline_prediction(
            team_1=pred['team_1'],
            team_2=pred['team_2'],
            prediction=pred['predicted_winner'],
            result=result['actual_winner'] if result else None,
            points=points_earned if points_earned > 0 else None,
            date_str=match_datetime.strftime("%B %d, %Y")
        )
    
    st.markdown("---")
    
    # Filters
    st.markdown('<h3>🔍 Filter Predictions</h3>', unsafe_allow_html=True)
    
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        stage_filter = st.multiselect(
            "Tournament Stage",
            options=sorted(predictions_df['stage'].unique().tolist())
        )
    
    with filter_col2:
        status_options = []
        if any(storage.has_result(p['match_id']) and 
               storage.get_match_result(p['match_id'])['actual_winner'] == p['predicted_winner'] 
               for _, p in predictions_df.iterrows()):
            status_options.append("Correct")
        if any(storage.has_result(p['match_id']) and 
               storage.get_match_result(p['match_id'])['actual_winner'] != p['predicted_winner'] 
               for _, p in predictions_df.iterrows()):
            status_options.append("Incorrect")
        if any(not storage.has_result(p['match_id']) for _, p in predictions_df.iterrows()):
            status_options.append("Pending")
        
        status_filter = st.multiselect(
            "Status",
            options=status_options
        )

except Exception as e:
    st.error(f"Error loading predictions: {e}")
