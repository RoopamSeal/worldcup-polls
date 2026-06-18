"""
Leaderboard page - Global rankings
"""
import streamlit as st
import pandas as pd
from src.config import Config
from src.storage import Storage

# Initialize
config = Config()
storage = Storage(config)
storage.initialize_data_layer()

st.set_page_config(page_title="Leaderboard - World Cup 2026", layout="wide")

st.title("🏆 Global Leaderboard")
st.markdown("---")

try:
    # Get leaderboard
    leaderboard = storage.get_leaderboard()
    
    if not leaderboard:
        st.info("Leaderboard will appear once players make predictions")
        st.stop()
    
    lb_df = pd.DataFrame(leaderboard)
    
    # Filters
    st.subheader("🔍 Filter & Sort")
    
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        min_predictions = st.slider(
            "Minimum Predictions",
            min_value=0,
            max_value=int(lb_df['total_predictions'].max()),
            value=0
        )
    
    with filter_col2:
        sort_by = st.radio(
            "Sort By",
            options=['Total Points', 'Accuracy %', 'Total Predictions', 'Rank'],
            horizontal=True
        )
    
    # Apply filters
    filtered_df = lb_df[lb_df['total_predictions'] >= min_predictions].copy()
    
    # Apply sorting
    if sort_by == 'Total Points':
        filtered_df = filtered_df.sort_values('total_points', ascending=False)
    elif sort_by == 'Accuracy %':
        filtered_df = filtered_df.sort_values('accuracy_percentage', ascending=False)
    elif sort_by == 'Total Predictions':
        filtered_df = filtered_df.sort_values('total_predictions', ascending=False)
    else:
        filtered_df = filtered_df.sort_values('rank')
    
    filtered_df['rank'] = range(1, len(filtered_df) + 1)
    
    # Display leaderboard
    st.markdown("---")
    st.subheader(f"📊 Leaderboard ({len(filtered_df)} Players)")
    
    # Create display dataframe
    display_df = filtered_df[[
        'rank', 'user_name', 'total_points', 'total_predictions',
        'correct_predictions', 'accuracy_percentage'
    ]].copy()
    
    display_df.columns = [
        'Rank', 'Player', 'Points', 'Predictions', 'Correct', 'Accuracy %'
    ]
    
    # Format display
    display_df['Rank'] = display_df['Rank'].astype(int)
    display_df['Points'] = display_df['Points'].astype(int)
    display_df['Predictions'] = display_df['Predictions'].astype(int)
    display_df['Correct'] = display_df['Correct'].astype(int)
    display_df['Accuracy %'] = display_df['Accuracy %'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Highlight user's rank
    if st.session_state.user_id:
        user_rank = storage.get_user_rank(st.session_state.user_id)
        if user_rank:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Your Rank", f"#{user_rank['rank']}")
            
            with col2:
                st.metric("Points", user_rank['total_points'])
            
            with col3:
                st.metric("Accuracy", f"{user_rank['accuracy_percentage']:.1f}%")
            
            with col4:
                st.metric("Predictions", user_rank['total_predictions'])
    
    st.markdown("---")
    
    # Statistics
    st.subheader("📈 Leaderboard Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", len(filtered_df))
    
    with col2:
        st.metric("Avg Predictions", f"{filtered_df['total_predictions'].mean():.1f}")
    
    with col3:
        st.metric("Avg Accuracy", f"{filtered_df['accuracy_percentage'].mean():.1f}%")
    
    with col4:
        st.metric("Top Score", int(filtered_df['total_points'].max()))

except Exception as e:
    st.error(f"Error loading leaderboard: {e}")
