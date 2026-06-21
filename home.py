"""
FIFA World Cup 2026 Polls - Home Page
"""

import streamlit as st
from datetime import datetime
import uuid

# Page config
st.set_page_config(
    page_title="FIFA World Cup 2026 Polls",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    body { background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%); }
    .stButton > button { background: linear-gradient(135deg, #ffb81c 0%, #ffa500 100%);
                         color: #1a472a; font-weight: 600; border: none; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# Header
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="font-size: 3rem; margin: 0; color: #1a472a;">⚽ WORLD CUP 2026</h1>
    <h2 style="color: #e53238; margin: 0.5rem 0; border: none;">PREDICTION POLLS</h2>
    <p style="color: #666; font-size: 1.1rem;">Vote on matches and earn points!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Import storage
try:
    from src.storage import get_storage
    storage = get_storage()
except Exception as e:
    st.error(f"Error loading storage: {e}")
    st.stop()

# Login/Register
if st.session_state.user_id is None:
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""
        <div style="padding: 2rem 0;">
            <h2 style="color: #1a472a; border: none;">Welcome to World Cup Polls!</h2>
            <p style="font-size: 1.1rem; color: #666;">
                Make predictions on FIFA World Cup 2026 matches and compete with others.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # ... (Three columns for PREDICT/EARN/WIN remain the same as your code) ...
    
    with col_right:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 1rem;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    border: 2px solid #ffb81c; position: sticky; top: 80px;">
            <h2 style="color: #1a472a; border: none; text-align: center;">🎬 JOIN NOW</h2>
        """, unsafe_allow_html=True)
        
        name = st.text_input("Your Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="john@example.com")
        
        if st.button("Register & Play", use_container_width=True, type="primary"):
            if name and email:
                # Updated method call
                user = storage.get_or_create_user_by_email(email, display_name=name)
                
                if user:
                    st.session_state.user_id = user['user_id']
                    st.session_state.user_name = user['user_name']
                    st.success("✅ Welcome! Redirecting...")
                    st.rerun()
                else:
                    st.error("Error creating account")
            else:
                st.error("Please enter name and email")
        
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Logged in - Dashboard
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ffb81c 0%, #e53238 100%);
               padding: 1.5rem; border-radius: 0.8rem; color: white; text-align: center;
               margin-bottom: 2rem;">
        <h2 style="color: white; border: none; margin: 0;">✅ Welcome, {st.session_state.user_name}!</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    stats = storage.get_user_stats(st.session_state.user_id)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("🎯 Predictions", stats['total_predictions'])
    with col2: st.metric("✅ Correct", stats['correct_predictions'])
    with col3: st.metric("📊 Accuracy", f"{stats.get('accuracy', 0):.1f}%")
    with col4: st.metric("⭐ Points", stats['total_points'])
    
    st.markdown("---")
    
    # Matches preview (Updated for IST)
    st.subheader("📋 Upcoming Matches")
    matches = storage.get_all_matches()
    active = [m for m in matches if m.get('status', '').lower() == 'scheduled']
    
    if active:
        for match in active[:5]:
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1: st.write(f"**{match['team_1']}**")
            with col2: st.write("vs")
            with col3: st.write(f"**{match['team_2']}**")
            
            # Use the new kickoff_time_ist column
            st.caption(f"📅 {match['match_date']} | 🕐 {match.get('kickoff_time_ist', match['kickoff_time'])} IST | {match['stage']}")
            st.divider()
    else:
        st.info("No upcoming matches")

    if st.button("Logout", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
