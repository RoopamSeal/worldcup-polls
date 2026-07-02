"""
Predict page - Make predictions on matches.
Predictions are only open for TODAY's matches (EST date).
Future-date matches are locked — predict on the day they are played.
"""

import streamlit as st
from src.config import Config
from src.storage import get_storage
from src.fixtures import FixtureLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="World Cup 2026 Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize config, storage, and fixtures (cached — single pool for entire app)
config = Config()
storage = get_storage()

fixture_loader = FixtureLoader(config)
fixture_loader.ensure_fixtures_loaded(storage)

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

st.markdown("""
<h1 style="text-align: center;">🎯 MAKE YOUR PREDICTIONS</h1>
<p style="text-align: center; color: #e53238; font-size: 1rem;">
    Predict today's matches before kickoff and earn points!
</p>
""", unsafe_allow_html=True)

st.markdown("---")

if st.session_state.user_id is None:
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1.5rem 1rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">👋</div>
        <p style="color: rgba(255,255,255,0.9); font-size: 0.95rem; line-height: 1.6; margin: 0;">
            Head to the <strong style="color: #ffb81c;">Home</strong> page to log in and start predicting!
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"""
    <div style="background: linear-gradient(135deg, #ffb81c 0%, #e53238 100%);
                padding: 1rem; border-radius: 0.8rem; text-align: center;
                margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
        <p style="color: white; font-size: 0.9rem; margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
            ✅ Logged In As
        </p>
        <p style="color: white; font-size: 1.4rem; margin: 0.5rem 0 0 0; font-weight: 800; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
            {st.session_state.user_name}
        </p>
    </div>
    """, unsafe_allow_html=True)

    user_predictions = storage.get_user_prediction_count(st.session_state.user_id)
    user_correct = storage.get_user_correct_predictions(st.session_state.user_id)
    user_points = storage.get_user_total_points(st.session_state.user_id)

    st.sidebar.markdown("### 📊 Your Stats")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("🎯 Preds", user_predictions)
        st.metric("⭐ Points", user_points)
    with col2:
        accuracy = (user_correct / user_predictions * 100) if user_predictions > 0 else 0
        st.metric("✅ Correct", user_correct)
        st.metric("📈 Acc %", f"{accuracy:.1f}%")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.rerun()

st.sidebar.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.6); font-size: 0.75rem; margin-top: 2rem;">
    ⚽ FIFA World Cup 2026<br>
    v1.0 | Powered by Data
</div>
""", unsafe_allow_html=True)

# Navigation — defines page titles shown in sidebar
pg = st.navigation([
    st.Page("home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/02_Predict.py", title="Predict", icon="⚽"),
    st.Page("pages/03_My_Predictions.py", title="My Predictions", icon="📊"),
    st.Page("pages/04_Leaderboard.py", title="Leaderboard", icon="🏆"),
    st.Page("pages/05_Admin.py", title="Admin", icon="⚙️"),
])
pg.run()
