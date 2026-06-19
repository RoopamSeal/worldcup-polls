"""
Home page - Tournament dashboard with FIFA 2026 design
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from src.config import Config
from src.storage import Storage
from src.fixtures import FixtureLoader

# Initialize
config = Config()
storage = Storage(config)
storage.initialize_data_layer()
fixture_loader = FixtureLoader(config)
fixture_loader.ensure_fixtures_loaded(storage)

st.set_page_config(page_title="Home - World Cup 2026", layout="wide")

st.markdown("""
<h1 style="text-align: center; font-size: 2.5rem; margin-bottom: 0;">
    ⚽ WORLD CUP 2026 DASHBOARD
</h1>
<p style="text-align: center; color: #e53238; font-size: 1.1rem; margin-bottom: 2rem;">
    🇺🇸 USA | 🇨🇦 CANADA | 🇲🇽 MEXICO
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Check authentication
if st.session_state.user_id is None:
    st.info("👈 Please log in using the sidebar to view the dashboard")
    st.stop()

# Tournament Info Section
st.markdown("""
<div style="background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%); 
            padding: 2rem; border-radius: 0.8rem; margin-bottom: 2rem;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; color: white; text-align: center;">
        <div>
            <p style="font-size: 0.9rem; color: #ffb81c; margin: 0;">TOURNAMENT</p>
            <h3 style="color: #ffffff; border: none; margin: 0.5rem 0; font-size: 1.4rem;">FIFA 2026</h3>
        </div>
        <div>
            <p style="font-size: 0.9rem; color: #ffb81c; margin: 0;">HOST NATIONS</p>
            <h3 style="color: #ffffff; border: none; margin: 0.5rem 0; font-size: 1.4rem;">3 Countries</h3>
        </div>
        <div>
            <p style="font-size: 0.9rem; color: #ffb81c; margin: 0;">TEAMS</p>
            <h3 style="color: #ffffff; border: none; margin: 0.5rem 0; font-size: 1.4rem;">32 Teams</h3>
        </div>
        <div>
            <p style="font-size: 0.9rem; color: #ffb81c; margin: 0;">MATCHES</p>
            <h3 style="color: #ffffff; border: none; margin: 0.5rem 0; font-size: 1.4rem;">64 Games</h3>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tournament Stats
st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>📊 Tournament Statistics</h2>", unsafe_allow_html=True)

try:
    tournament_stats = storage.get_tournament_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        users = tournament_stats.get('Total Users', '0')
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #ffb81c; margin: 0; font-size: 0.9rem;">👥 Users</p>
            <h3 style="color: #ffb81c; border: none; margin: 0.5rem 0; font-size: 2rem;">{users}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        matches = tournament_stats.get('Total Matches', '0')
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #ffb81c; margin: 0; font-size: 0.9rem;">🎯 Matches</p>
            <h3 style="color: #ffb81c; border: none; margin: 0.5rem 0; font-size: 2rem;">{matches}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        scheduled = tournament_stats.get('Scheduled Matches', '0')
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #ffb81c; margin: 0; font-size: 0.9rem;">🔜 Upcoming</p>
            <h3 style="color: #ffb81c; border: none; margin: 0.5rem 0; font-size: 2rem;">{scheduled}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        completed = tournament_stats.get('Completed Matches', '0')
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #ffb81c; margin: 0; font-size: 0.9rem;">✅ Completed</p>
            <h3 style="color: #ffb81c; border: none; margin: 0.5rem 0; font-size: 2rem;">{completed}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        predictions = tournament_stats.get('Total Predictions', '0')
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #ffb81c; margin: 0; font-size: 0.9rem;">⭐ Predictions</p>
            <h3 style="color: #ffb81c; border: none; margin: 0.5rem 0; font-size: 2rem;">{predictions}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
except Exception as e:
    st.warning(f"Could not load tournament stats: {e}")

# Today's/Upcoming Matches
st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>🔜 Upcoming Matches</h2>", unsafe_allow_html=True)

try:
    matches = storage.get_all_matches()
    matches_df = pd.DataFrame(matches)
    
    if matches_df.empty:
        st.info("No matches scheduled yet")
    else:
        # Filter active matches (scheduled or live)
        active_matches = matches_df[matches_df['status'].isin(['scheduled', 'live'])]
        
        if active_matches.empty:
            st.info("No upcoming matches")
        else:
            # Sort by date and time
            active_matches = active_matches.copy()
            active_matches['match_datetime'] = pd.to_datetime(
                active_matches['match_date'] + ' ' + active_matches['kickoff_time']
            )
            active_matches = active_matches.sort_values('match_datetime')
            
            for idx, (_, match) in enumerate(active_matches.head(10).iterrows()):
                match_datetime = pd.to_datetime(
                    f"{match['match_date']} {match['kickoff_time']}"
                )
                
                st.markdown(f"""
                <div class="match-card">
                    <div style="display: grid; grid-template-columns: 2fr 1fr 2fr 1.5fr; gap: 1rem; align-items: center;">
                        <div style="text-align: right;">
                            <h4 style="color: #1a472a; margin: 0; font-size: 1.1rem; font-weight: 700;">
                                {match['team_1']}
                            </h4>
                        </div>
                        <div style="text-align: center;">
                            <span style="background: #ffb81c; color: #1a472a; padding: 0.5rem 0.8rem; 
                                       border-radius: 0.4rem; font-weight: 600; font-size: 0.85rem;">
                                vs
                            </span>
                        </div>
                        <div style="text-align: left;">
                            <h4 style="color: #1a472a; margin: 0; font-size: 1.1rem; font-weight: 700;">
                                {match['team_2']}
                            </h4>
                        </div>
                        <div style="text-align: center;">
                            <p style="color: #666; margin: 0; font-size: 0.9rem;">
                                📅 {match_datetime.strftime('%b %d')}<br>
                                🕐 {match_datetime.strftime('%H:%M')}<br>
                                📍 {match['venue']}
                            </p>
                        </div>
                    </div>
                    <div style="margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid #e0e0e0;">
                        <span style="background: #e53238; color: white; padding: 0.3rem 0.6rem; 
                                   border-radius: 0.3rem; font-size: 0.8rem; font-weight: 600;">
                            {match['stage']}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error loading matches: {e}")

st.markdown("---")

# Leaderboard Preview
st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>🏆 Top 10 Leaderboard</h2>", unsafe_allow_html=True)

try:
    leaderboard = storage.get_leaderboard(limit=10)
    
    if leaderboard:
        lb_df = pd.DataFrame(leaderboard)
        
        # Format display
        display_df = lb_df[[
            'rank', 'user_name', 'total_points', 'accuracy_percentage'
        ]].copy()
        
        display_df.columns = [
            '🏅', 'Player', '⭐ Points', '📊 Accuracy %'
        ]
        
        # Add emoji medals
        display_df['🏅'] = display_df['🏅'].apply(lambda x: 
            '🥇' if x == 1 else '🥈' if x == 2 else '🥉' if x == 3 else f'#{x}'
        )
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("Leaderboard will appear once users make predictions")
except Exception as e:
    st.error(f"Error loading leaderboard: {e}")

st.markdown("---")

# User's Stats
if st.session_state.user_id:
    st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>👤 Your Statistics</h2>", unsafe_allow_html=True)
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        predictions = storage.get_user_prediction_count(st.session_state.user_id)
        correct = storage.get_user_correct_predictions(st.session_state.user_id)
        accuracy = (correct / predictions * 100) if predictions > 0 else 0
        points = storage.get_user_total_points(st.session_state.user_id)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #ffb81c; margin: 0; font-size: 0.9rem;">🎯 Predictions</p>
                <h3 style="color: #ffb81c; border: none; margin: 0.5rem 0; font-size: 2rem;">{predictions}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #ffb81c; margin: 0; font-size: 0.9rem;">✅ Correct</p>
                <h3 style="color: #ffb81c; border: none; margin: 0.5rem 0; font-size: 2rem;">{correct}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #ffb81c; margin: 0; font-size: 0.9rem;">📊 Accuracy</p>
                <h3 style="color: #ffb81c; border: none; margin: 0.5rem 0; font-size: 2rem;">{accuracy:.1f}%</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #ffb81c; margin: 0; font-size: 0.9rem;">⭐ Total Points</p>
                <h3 style="color: #ffb81c; border: none; margin: 0.5rem 0; font-size: 2rem;">{points}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # User rank
        user_rank = storage.get_user_rank(st.session_state.user_id)
        if user_rank:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffb81c 0%, #ffa500 100%); 
                        padding: 1.5rem; border-radius: 0.8rem; text-align: center;
                        color: #1a472a; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                <h3 style="color: #1a472a; border: none; margin: 0; font-size: 1.8rem;">
                    🎯 Rank #{user_rank['rank']}
                </h3>
                <p style="margin: 0.5rem 0 0 0; font-weight: 600;">You're in the top {(user_rank['rank'] / len(storage.get_leaderboard())) * 100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading user stats: {e}")

st.markdown("---")

# Information Section
st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>ℹ️ How to Play</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="prediction-card">
        <h3 style="color: #e53238; border: none; margin-top: 0;">🎯 Make Predictions</h3>
        <ul style="color: #666; margin: 0;">
            <li>Go to the <b>Predict</b> page</li>
            <li>Choose upcoming matches</li>
            <li>Select your predicted winner</li>
            <li>Lock in before kickoff</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="prediction-card">
        <h3 style="color: #e53238; border: none; margin-top: 0;">📊 Track Performance</h3>
        <ul style="color: #666; margin: 0;">
            <li>Visit <b>My Predictions</b></li>
            <li>View your prediction history</li>
            <li>Check accuracy metrics</li>
            <li>Earn points for correct picks</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="prediction-card">
        <h3 style="color: #e53238; border: none; margin-top: 0;">🏆 Climb Rankings</h3>
        <ul style="color: #666; margin: 0;">
            <li>Check the <b>Leaderboard</b></li>
            <li>Compete globally</li>
            <li>Earn achievement badges</li>
            <li>Have fun! ⚽</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Scoring Info
st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>⭐ Scoring System</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); 
                padding: 1.5rem; border-radius: 0.8rem; text-align: center;
                color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h3 style="color: #ffffff; border: none; margin: 0;">✅ CORRECT</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;">+3 POINTS</p>
        <small>Predict the winner correctly</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffb81c 0%, #ffa500 100%); 
                padding: 1.5rem; border-radius: 0.8rem; text-align: center;
                color: #1a472a; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h3 style="color: #1a472a; border: none; margin: 0;">🤝 DRAW</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;">+2 POINTS</p>
        <small>Predict a draw correctly</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e53238 0%, #c41e3a 100%); 
                padding: 1.5rem; border-radius: 0.8rem; text-align: center;
                color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h3 style="color: #ffffff; border: none; margin: 0;">❌ INCORRECT</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;">0 POINTS</p>
        <small>Wrong prediction</small>
    </div>
    """, unsafe_allow_html=True)
