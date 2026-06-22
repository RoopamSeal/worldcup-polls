"""
Leaderboard page — Top 10 global rankings.
"""

import streamlit as st
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Leaderboard", layout="wide")

st.markdown("""
<h1 style="text-align: center;">🏆 GLOBAL LEADERBOARD</h1>
<p style="text-align: center; color: #e53238; font-size: 1rem;">
    Top 10 players worldwide
</p>
""", unsafe_allow_html=True)
st.markdown("---")

try:
    from src.storage import get_storage
    storage = get_storage()
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.stop()

try:
    leaderboard = storage.get_leaderboard(limit=10)

    if not leaderboard:
        st.info("📊 Leaderboard will appear once players make predictions.")
        st.stop()

    df = pd.DataFrame(leaderboard)

    # ── Podium (top 3) ─────────────────────────────────────────────
    st.markdown("<h3 style='color:#1a472a; border:none;'>🥇🥈🥉 Podium</h3>", unsafe_allow_html=True)
    podium_cols = st.columns(3)
    medals = [
        ("🥇", "1st", "linear-gradient(135deg,#ffb81c,#ffa500)", "#1a472a"),
        ("🥈", "2nd", "linear-gradient(135deg,#c0c0c0,#a8a8a8)", "#ffffff"),
        ("🥉", "3rd", "linear-gradient(135deg,#cd7f32,#b87333)", "#ffffff"),
    ]
    for i, (icon, label, bg, color) in enumerate(medals):
        if i < len(df):
            row = df.iloc[i]
            acc = row.get('accuracy_percentage', row.get('accuracy', 0))
            with podium_cols[i]:
                st.markdown(f"""
<div style="background:{bg}; padding:1.5rem; border-radius:0.8rem;
            text-align:center; box-shadow:0 6px 20px rgba(0,0,0,0.15);">
  <h1 style="color:{color}; border:none; margin:0;">{icon}</h1>
  <h3 style="color:{color}; border:none; margin:0.5rem 0;">{label} Place</h3>
  <h2 style="color:{color}; border:none; margin:0.5rem 0; font-size:1.2rem;">{row['user_name']}</h2>
  <div style="background:rgba(0,0,0,0.1); padding:0.8rem; border-radius:0.5rem; margin-top:1rem;">
    <p style="color:{color}; margin:0; font-weight:600;">⭐ {int(row['total_points'])} Points</p>
    <p style="color:{color}; margin:0.3rem 0 0; font-size:0.9rem;">📊 {float(acc):.1f}% Accuracy</p>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Full top-10 table ──────────────────────────────────────────
    st.markdown("<h3 style='color:#1a472a; border:none;'>📊 Top 10 Rankings</h3>", unsafe_allow_html=True)

    display_df = df[['rank', 'user_name', 'total_points', 'total_predictions',
                      'correct_predictions', 'accuracy_percentage']].copy()
    display_df.columns = ['🏅', 'Player', '⭐ Points', '🎯 Preds', '✅ Correct', '📊 Accuracy %']
    display_df['🏅'] = display_df['🏅'].apply(
        lambda x: '🥇' if x == 1 else '🥈' if x == 2 else '🥉' if x == 3 else f'#{x}'
    )
    display_df['📊 Accuracy %'] = display_df['📊 Accuracy %'].apply(lambda x: f"{float(x):.1f}%")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── Current user's rank ────────────────────────────────────────
    if st.session_state.get('user_id'):
        st.markdown("---")
        st.markdown("<h3 style='color:#1a472a; border:none;'>👤 Your Ranking</h3>", unsafe_allow_html=True)
        user_rank = storage.get_user_rank(st.session_state.user_id)
        if user_rank:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🏅 Rank",    f"#{user_rank['rank']}")
            col2.metric("⭐ Points",  int(user_rank['total_points']))
            col3.metric("📊 Accuracy", f"{float(user_rank.get('accuracy_percentage', 0)):.1f}%")
            col4.metric("🎯 Preds",   int(user_rank['total_predictions']))

    now = datetime.now().strftime("%H:%M:%S")
    st.caption(f"🔄 Updated at {now}")

except Exception as e:
    logger.error(f"Leaderboard error: {e}", exc_info=True)
    st.error(f"Error: {str(e)}")
