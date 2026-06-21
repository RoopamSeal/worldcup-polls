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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style="background: #e8f5e9; padding: 1.5rem; border-radius: 0.8rem;
                       border-left: 5px solid #4caf50;">
                <h3 style="color: #4caf50; border: none; margin-top: 0;">🎯 PREDICT</h3>
                <p style="color: #666; margin: 0;">Vote on match winners</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: #fff3e0; padding: 1.5rem; border-radius: 0.8rem;
                       border-left: 5px solid #ff9800;">
                <h3 style="color: #ff9800; border: none; margin-top: 0;">⭐ EARN</h3>
                <p style="color: #666; margin: 0;">Gain points for correct predictions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: #fce4ec; padding: 1.5rem; border-radius: 0.8rem;
                       border-left: 5px solid #e91e63;">
                <h3 style="color: #e91e63; border: none; margin-top: 0;">🏆 WIN</h3>
                <p style="color: #666; margin: 0;">Top the leaderboard</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 1rem;
                   box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                   border: 2px solid #ffb81c; position: sticky; top: 80px;">
            <h2 style="color: #1a472a; border: none; text-align: center;">🎬 JOIN NOW</h2>
        """, unsafe_allow_html=True)
        
        name = st.text_input("Your Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="john@example.com")
        country = st.selectbox("Favorite Team Country", 
                              ["Argentina", "Brazil", "France", "Germany", "England", "Spain", "Other"])
        
        if st.button("Register & Play", use_container_width=True, type="primary"):
            if name and email:
                user_id = str(uuid.uuid4())
                user = storage.get_or_create_user(user_id, name, email, country)
                
                if user:
                    st.session_state.user_id = user_id
                    st.session_state.user_name = name
                    st.success("✅ Welcome! Redirecting...")
                    st.rerun()
                else:
                    st.error("Error creating account")
            else:
                st.error("Please enter name and email")
        
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Logged in - Show dashboard
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ffb81c 0%, #e53238 100%);
               padding: 1.5rem; border-radius: 0.8rem; color: white; text-align: center;
               margin-bottom: 2rem;">
        <h2 style="color: white; border: none; margin: 0;">
            ✅ Welcome, {st.session_state.user_name}!
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    stats = storage.get_user_stats(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Predictions", stats['total_predictions'])
    with col2:
        st.metric("✅ Correct", stats['correct_predictions'])
    with col3:
        st.metric("📊 Accuracy", f"{stats['accuracy']:.1f}%")
    with col4:
        st.metric("⭐ Points", stats['total_points'])
    
    st.markdown("---")
    
    # Matches preview
    st.subheader("📋 Upcoming Matches")
    
    matches = storage.get_all_matches()
    active = [m for m in matches if m.get('status', '').lower() == 'scheduled']
    
    if active:
        st.success(f"Found {len(active)} upcoming matches")
        
        # Show first 5
        for i, match in enumerate(active[:5]):
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.write(f"**{match['team_1']}**")
            with col2:
                st.write("vs")
            with col3:
                st.write(f"**{match['team_2']}**")
            
            st.caption(f"📅 {match['match_date']} | 🕐 {match['kickoff_time']} | {match['stage']}")
            st.divider()
    else:
        st.info("No upcoming matches")
    
    # Logout
    if st.button("Logout", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>⚽ FIFA World Cup 2026 Polls | All times in IST</p>", 
           unsafe_allow_html=True)
