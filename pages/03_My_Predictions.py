"""
My Predictions page - View prediction history
"""
import streamlit as st
import pandas as pd
from src.config import Config
from src.storage import Storage

# Initialize
config = Config()
storage = Storage(config)
storage.initialize_data_layer()

st.set_page_config(page_title="My Predictions - World Cup 2026", layout="wide")

st.title("📊 My Predictions")
st.markdown("---")

# Check authentication
if st.session_state.user_id is None:
    st.info("Please log in from the Home page to view your predictions")
    st.stop()

try:
    # Get user's predictions
    predictions = storage.get_user_predictions(st.session_state.user_id)
    
    if not predictions:
        st.info("You haven't made any predictions yet. Go to the Predict page to get started!")
        st.stop()
    
    predictions_df = pd.DataFrame(predictions)
    
    # Get match information
    all_matches = pd.DataFrame(storage.get_all_matches())
    
    # Get results
    all_results = pd.DataFrame(storage.get_match_result(m['match_id']) for m in storage.get_all_matches() 
                               if storage.has_result(m['match_id']))
    
    # Merge data
    predictions_df = predictions_df.merge(
        all_matches[['match_id', 'team_1', 'team_2', 'match_date', 'kickoff_time', 'stage']],
        on='match_id',
        how='left'
    )
    
    # Sort by date descending
    predictions_df = predictions_df.sort_values('prediction_timestamp', ascending=False)
    
    # Display stats
    st.subheader("Your Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Predictions", len(predictions_df))
    
    with col2:
        # Count correct predictions
        correct = 0
        for _, pred in predictions_df.iterrows():
            result = storage.get_match_result(pred['match_id'])
            if result and result['actual_winner'] == pred['predicted_winner']:
                correct += 1
        st.metric("Correct", correct)
    
    with col3:
        accuracy = (correct / len(predictions_df) * 100) if len(predictions_df) > 0 else 0
        st.metric("Accuracy %", f"{accuracy:.1f}%")
    
    with col4:
        points = storage.get_user_total_points(st.session_state.user_id)
        st.metric("Total Points", points)
    
    st.markdown("---")
    
    # Display predictions table
    st.subheader("Prediction History")
    
    # Create display dataframe
    display_data = []
    
    for _, pred in predictions_df.iterrows():
        result = storage.get_match_result(pred['match_id'])
        
        match_datetime = pd.to_datetime(f"{pred['match_date']} {pred['kickoff_time']}")
        
        if result:
            is_correct = result['actual_winner'] == pred['predicted_winner']
            status = "✅ Correct" if is_correct else "❌ Wrong"
            actual = result['actual_winner']
        else:
            status = "⏳ Pending"
            actual = "-"
        
        display_data.append({
            'Date': match_datetime.strftime("%m/%d %H:%M"),
            'Match': f"{pred['team_1']} vs {pred['team_2']}",
            'Stage': pred['stage'],
            'Your Prediction': pred['predicted_winner'],
            'Actual Result': actual,
            'Status': status
        })
    
    display_df = pd.DataFrame(display_data)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Filters
    st.subheader("🔍 Filter Predictions")
    
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        stage_filter = st.multiselect(
            "Tournament Stage",
            options=predictions_df['stage'].unique().tolist()
        )
    
    with filter_col2:
        status_filter = st.multiselect(
            "Prediction Status",
            options=['Correct', 'Incorrect', 'Pending']
        )
    
    # Apply filters
    filtered_df = predictions_df.copy()
    
    if stage_filter:
        filtered_df = filtered_df[filtered_df['stage'].isin(stage_filter)]
    
    if filtered_df.empty:
        st.info("No predictions match the selected filters")
    else:
        st.write(f"Showing {len(filtered_df)} predictions")

except Exception as e:
    st.error(f"Error loading predictions: {e}")
