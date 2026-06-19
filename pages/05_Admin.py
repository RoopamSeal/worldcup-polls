"""
Admin page - Administrative functions with FIFA 2026 design
"""
import streamlit as st
import pandas as pd
from src.config import Config
from src.storage import Storage
from src.fixtures import FixtureLoader, create_sample_fixtures
from src.simulator import ResultSimulator
from src.leaderboard import LeaderboardManager

# Initialize
config = Config()
storage = Storage(config)
storage.initialize_data_layer()

st.set_page_config(page_title="Admin - World Cup 2026", layout="wide")

st.markdown("""
<h1 style="text-align: center;">⚙️ ADMIN CONSOLE</h1>
<p style="text-align: center; color: #e53238; font-size: 1rem;">
    Manage tournament data and settings
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Simple auth - check if admin
admin_password = st.secrets.get("admin_password", "admin123")

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e53238 0%, #c41e3a 100%); 
                padding: 2rem; border-radius: 0.8rem; text-align: center;
                color: white; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
        <h2 style="color: #ffb81c; border: none; margin: 0;">🔒 ADMIN ACCESS REQUIRED</h2>
        <p style="margin: 1rem 0 0 0;">Please authenticate to access admin features</p>
    </div>
    """, unsafe_allow_html=True)
    
    password = st.text_input("Enter admin password:", type="password", help="Contact admin for password")
    
    if st.button("🔓 Authenticate", use_container_width=True, type="primary"):
        if password == admin_password:
            st.session_state.admin_authenticated = True
            st.success("✅ Authenticated successfully!")
            st.rerun()
        else:
            st.error("❌ Invalid password")
    st.stop()

st.markdown("""
<div style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); 
            padding: 1rem; border-radius: 0.8rem; margin-bottom: 1.5rem;
            color: white; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <p style="margin: 0; font-weight: 600;">✅ ADMIN MODE ACTIVE</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Admin tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Database",
    "🎯 Fixtures",
    "🎮 Simulator",
    "🏆 Leaderboard",
    "🔧 Maintenance"
])

# ========== TAB 1: Database ==========
with tab1:
    st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>📊 Database Management</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='color: #1a472a; border: none;'>📈 Table Statistics</h3>", unsafe_allow_html=True)
        try:
            sizes = storage.get_database_size()
            for name, count in sizes.items():
                st.metric(f"📋 {name.capitalize()}", count)
        except Exception as e:
            st.error(f"Error: {e}")
    
    with col2:
        st.markdown("<h3 style='color: #1a472a; border: none;'>👀 Data Preview</h3>", unsafe_allow_html=True)
        
        table_choice = st.selectbox(
            "Select table to preview",
            ["users", "matches", "predictions", "results", "points"]
        )
        
        try:
            if table_choice == "users":
                df = pd.read_csv(config.USER_MASTER_PATH)
            elif table_choice == "matches":
                df = pd.read_csv(config.MATCH_MASTER_PATH)
            elif table_choice == "predictions":
                df = pd.read_csv(config.PREDICTION_FACT_PATH)
            elif table_choice == "results":
                df = pd.read_csv(config.MATCH_RESULT_PATH)
            else:
                df = pd.read_csv(config.POINTS_FACT_PATH)
            
            st.dataframe(df.head(5), use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

# ========== TAB 2: Fixtures ==========
with tab2:
    st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>🎯 Fixture Management</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='color: #1a472a; border: none;'>📋 Current Status</h3>", unsafe_allow_html=True)
        try:
            matches = storage.get_all_matches()
            st.metric("🎯 Total Matches", len(matches))
            
            if matches:
                matches_df = pd.DataFrame(matches)
                st.write("**Status Breakdown:**")
                st.json(matches_df['status'].value_counts().to_dict())
        except Exception as e:
            st.error(f"Error: {e}")
    
    with col2:
        st.markdown("<h3 style='color: #1a472a; border: none;'>⚡ Load Fixtures</h3>", unsafe_allow_html=True)
        
        if st.button("📥 Load Sample Fixtures", use_container_width=True, type="primary"):
            try:
                fixtures_df = create_sample_fixtures()
                storage.load_fixtures(fixtures_df)
                st.success(f"✅ Loaded {len(fixtures_df)} sample fixtures!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Upload custom fixtures
    st.markdown("<h3 style='color: #1a472a; border: none;'>📤 Upload Custom Fixtures</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    
    if uploaded_file:
        try:
            fixtures_df = pd.read_csv(uploaded_file)
            st.dataframe(fixtures_df)
            
            if st.button("✅ Load Uploaded Fixtures", use_container_width=True, type="primary"):
                fixture_loader = FixtureLoader(config)
                if fixture_loader.validate_fixtures(fixtures_df):
                    storage.load_fixtures(fixtures_df)
                    st.success(f"✅ Loaded {len(fixtures_df)} fixtures!")
                else:
                    st.error("❌ Fixture validation failed")
        except Exception as e:
            st.error(f"Error: {e}")

# ========== TAB 3: Simulator ==========
with tab3:
    st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>🎮 Match Result Simulator</h2>", unsafe_allow_html=True)
    
    simulator = ResultSimulator(config, storage)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⚡ Auto-Simulate Completed Matches", use_container_width=True, type="primary"):
            try:
                count = simulator.auto_simulate_completed_matches()
                st.success(f"✅ Simulated {count} matches")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("🔴 BULK SIMULATE ALL RESULTS", use_container_width=True):
            if st.checkbox("⚠️ Confirm bulk simulation (This will simulate ALL matches)"):
                try:
                    count = simulator.bulk_simulate_all_results()
                    st.success(f"✅ Simulated {count} matches")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.markdown("---")
    
    st.markdown("<h3 style='color: #1a472a; border: none;'>✍️ Manual Result Entry</h3>", unsafe_allow_html=True)
    
    try:
        matches = storage.get_matches_by_status('scheduled')
        if matches:
            match_dict = {f"{m['team_1']} vs {m['team_2']}": m for m in matches}
            
            selected_match_str = st.selectbox(
                "Select match",
                list(match_dict.keys())
            )
            
            selected_match = match_dict[selected_match_str]
            
            winner = st.radio(
                "Winner",
                [selected_match['team_1'], selected_match['team_2'], 'draw'],
                horizontal=True
            )
            
            if st.button("💾 Save Result", use_container_width=True, type="primary"):
                storage.save_match_result(selected_match['match_id'], winner)
                storage.update_match_status(selected_match['match_id'], 'completed')
                st.success("✅ Result saved!")
        else:
            st.info("No scheduled matches")
    except Exception as e:
        st.error(f"Error: {e}")

# ========== TAB 4: Leaderboard ==========
with tab4:
    st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>🏆 Leaderboard Management</h2>", unsafe_allow_html=True)
    
    leaderboard_mgr = LeaderboardManager(config, storage)
    
    if st.button("🔄 Refresh Leaderboard Now", use_container_width=True, type="primary"):
        try:
            leaderboard_mgr.refresh_all_gold_tables()
            st.success("✅ Leaderboard refreshed successfully!")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    
    st.markdown("<h3 style='color: #1a472a; border: none;'>📊 Current Leaderboard</h3>", unsafe_allow_html=True)
    
    try:
        leaderboard = storage.get_leaderboard()
        if leaderboard:
            lb_df = pd.DataFrame(leaderboard)
            st.dataframe(
                lb_df[[
                    'rank', 'user_name', 'total_points',
                    'total_predictions', 'accuracy_percentage'
                ]],
                use_container_width=True
            )
        else:
            st.info("Leaderboard empty")
    except Exception as e:
        st.error(f"Error: {e}")

# ========== TAB 5: Maintenance ==========
with tab5:
    st.markdown("<h2 style='color: #1a472a; border-bottom: 3px solid #ffb81c;'>🔧 Maintenance & Settings</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='color: #1a472a; border: none;'>📊 Tournament Stats</h3>", unsafe_allow_html=True)
        if st.button("📈 View Statistics", use_container_width=True):
            try:
                stats = storage.get_tournament_stats()
                for key, value in stats.items():
                    st.metric(key, value)
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        st.markdown("<h3 style='color: #1a472a; border: none;'>⚠️ Dangerous Zone</h3>", unsafe_allow_html=True)
        
        st.warning("🔴 Reset all data? This cannot be undone!")
        
        if st.checkbox("Enable reset function"):
            if st.button("🔴 RESET ALL TABLES", use_container_width=True):
                try:
                    storage.reset_all_tables()
                    st.success("✅ All tables have been reset!")
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.8rem;">
    Admin Console | Use with caution | Last activity logged
</div>
""", unsafe_allow_html=True)
