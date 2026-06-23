"""
User Guide page - Instructions and FAQ for the platform.
"""

import streamlit as st

st.set_page_config(page_title="User Guide", page_icon="📖", layout="wide")

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

if 'ab_group' not in st.session_state:
    st.session_state.ab_group = 'control'
# ==========================================

# Header
st.markdown("""
<div style="background:linear-gradient(135deg,#1a472a 0%,#2d5a3d 60%,#1a472a 100%);
     padding:2rem; border-radius:1.2rem; text-align:center; margin-bottom:2rem;
     box-shadow:0 6px 24px rgba(26,71,42,0.25);">
  <h1 style="color:#ffffff; border:none; padding:0; margin:0; font-size:2.2rem; font-weight:900;">
      📖 OFFICIAL USER GUIDE
  </h1>
  <p style="color:#ffb81c; margin:0.4rem 0 0; font-size:1rem; letter-spacing:1px;">
      Everything you need to know to dominate the 2026 World Cup predictions.
  </p>
</div>
""", unsafe_allow_html=True)

# Create Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 Getting Started", 
    "🎯 How to Predict", 
    "⭐ Scoring & Ranks", 
    "❓ FAQ"
])

with tab1:
    st.markdown("<h3 style='color:#1a472a;'>Welcome to the Tournament!</h3>", unsafe_allow_html=True)
    st.write("""
    This platform allows you to predict the outcome of all 104 matches of the FIFA World Cup 2026. 
    Compete against friends and fans worldwide to see who has the best football intuition.
    """)
    
    st.markdown("#### 1. Account Creation & Login")
    st.write("""
    * **No Passwords Required:** We use a simple, passwordless login system. 
    * **New Users:** Enter your email and choose a "Display Name" on the Home page. Your Display Name is how you will appear on the global leaderboard.
    * **Returning Users:** Simply enter your registered email on the Home page and click "Join Now" to instantly access your dashboard.
    """)
    
    st.info("💡 **Tip:** If you forget your Display Name or aren't sure which email you used, use the 'Forgot your display name?' search tool on the Home page.")

with tab2:
    st.markdown("<h3 style='color:#1a472a;'>Making & Managing Predictions</h3>", unsafe_allow_html=True)
    
    st.markdown("#### The Rules of Prediction")
    st.write("""
    1. Navigate to the **Predict** page using the sidebar.
    2. Use the dropdown menu to select the specific match date.
    3. Click the button corresponding to your choice: **Team A Win**, **DRAW**, or **Team B Win**.
    4. Once clicked, your prediction is instantly saved to the database.
    """)
    
    st.warning("⏱️ **The Deadline:** You can make or change your predictions *up until the exact minute the match kicks off*. Once the match starts, predictions for that game are locked permanently.")
    
    st.markdown("#### Tracking Your Picks")
    st.write("""
    You can view your entire prediction history on the **My Predictions** page. This dashboard will show you exactly what you picked, what the actual result was, and how many points you earned for each completed match.
    """)

with tab3:
    st.markdown("<h3 style='color:#1a472a;'>The Scoring System</h3>", unsafe_allow_html=True)
    st.write("Points are awarded automatically as soon as a real-world match finishes and the system syncs with the official FIFA results.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("**✅ Correct Winner (+3 Points)**\nYou correctly predicted which team would win the match.")
    with col2:
        st.warning("**🤝 Correct Draw (+2 Points)**\nYou correctly predicted the match would end in a tie (after 90 mins / extra time depending on the tournament stage).")
    with col3:
        st.error("**❌ Incorrect Pick (0 Points)**\nYour predicted outcome did not happen.")

    st.markdown("---")
    st.markdown("#### How the Leaderboard Works")
    st.write("""
    The **Leaderboard** ranks all users globally based on their Total Points. 
    * **Tie-Breakers:** If two players have the exact same number of points, the player with the higher total number of *Correct Predictions* will be ranked higher.
    * **Your Rank:** You can check your personal global rank and percentile (e.g., "Top 10%") on your Home dashboard.
    """)

with tab4:
    st.markdown("<h3 style='color:#1a472a;'>Frequently Asked Questions</h3>", unsafe_allow_html=True)
    
    with st.expander("🌍 What timezone are the match times in?"):
        st.write("All match kickoff times on the platform are displayed in **IST (Indian Standard Time)** to ensure a unified schedule for all players.")
        
    with st.expander("🔄 Can I change my prediction?"):
        st.write("**Yes!** If the match has not started yet, you can simply go to the Predict page and click a different button. Your new prediction will overwrite the old one. Once the match kicks off, changes are disabled.")
        
    with st.expander("🏆 What happens during knockout stages (penalties)?"):
        st.write("During the knockout stages, a match cannot end in a draw. The 'Winner' is determined by the team that advances to the next round, regardless of whether they won in regular time, extra time, or via penalty shootouts. Make sure you pick a clear winner for these games!")
        
    with st.expander("🛠️ The app is showing an error or won't load my profile."):
        st.write("If you experience a glitch, the fastest way to fix it is to refresh the webpage or clear your browser's cache. If you were logged out, simply return to the Home page and re-enter your email.")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#666; font-size:0.9rem;'>Need more help? Reach out to the tournament administrator.</p>", unsafe_allow_html=True)
