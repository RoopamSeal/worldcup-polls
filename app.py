import streamlit as st
import pandas as pd
import time

# --- Configuration & Styling ---
st.set_page_config(
    page_title="FIFA World Cup 2026 Poll",
    page_icon="⚽",
    layout="wide" 
)

# Custom CSS to make the interface feel more engaging and pad the columns
st.markdown("""
    <style>
    .stRadio > label { font-size: 18px; font-weight: bold; }
    .leaderboard-header { font-size: 24px; font-weight: bold; color: #FFD700; }
    </style>
""", unsafe_allow_html=True)

# --- Layout: 2 Columns (Left: Polls, Right: Leaderboard) ---
# The left column is wider (ratio 2:1)
left_col, right_col = st.columns([2, 1], gap="large")

# ==========================================
# LEFT COLUMN: Polling Interface
# ==========================================
with left_col:
    st.title("🏆 FIFA World Cup 2026 Poll")
    
    # Username Input
    username = st.text_input("Enter your Username to vote:", placeholder="e.g., Roopam")
    
    st.divider() # Visual separator
    
    if not username:
        st.info("👋 Welcome! Please enter your username above to start predicting.")
    else:
        st.subheader("🏟️ Today's Matches")
        
        # --- Match 1 ---
        st.markdown("### 🇸🇦 Saudi Arabia vs Uruguay 🇺🇾")
        m1_choice = st.radio(
            "Prediction for Match 1:",
            ["Saudi Arabia", "Uruguay", "Draw"],
            key="match_1",
            label_visibility="collapsed" # Hides the label for a cleaner look
        )
        if st.button("Vote ⚽", key="btn_m1", type="primary", use_container_width=True):
            with st.spinner("Recording vote..."):
                time.sleep(0.5) # Simulate network request
            st.toast(f"Vote for {m1_choice} recorded!", icon="✅")
            st.balloons() # Engaging celebration animation
            
        st.divider()
        
        # --- Match 2 ---
        # Duplicating the match structure based on your wireframe
        st.markdown("### 🇸🇦 Saudi Arabia vs Uruguay 🇺🇾") 
        m2_choice = st.radio(
            "Prediction for Match 2:",
            ["Saudi Arabia", "Uruguay", "Draw"],
            key="match_2",
            label_visibility="collapsed"
        )
        if st.button("Vote ⚽", key="btn_m2", type="primary", use_container_width=True):
            with st.spinner("Recording vote..."):
                time.sleep(0.5)
            st.toast(f"Vote for {m2_choice} recorded!", icon="✅")


# ==========================================
# RIGHT COLUMN: Leaderboard
# ==========================================
with right_col:
    st.header("🏅 Leaderboard")
    st.write("Top 5 Predictors")
    
    # Mock data for the Leaderboard
    # In a real app, you would calculate this from your votes.csv file
    leaderboard_data = pd.DataFrame({
        "Rank": ["🥇 1st", "🥈 2nd", "🥉 3rd", "4th", "5th"],
        "User": ["Roopam", "Alex_99", "Sarah_Goals", "MessiFan10", "JohnDoe"],
        "Points": [120, 105, 90, 85, 70]
    })
    
    # Display as a clean, interactive dataframe
    st.dataframe(
        leaderboard_data,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Points": st.column_config.NumberColumn(
                "Points",
                help="Total points earned from correct predictions",
                format="%d ⭐"
            )
        }
    )
    
    # Add a fun fact or status box below the leaderboard
    st.info("💡 **Pro Tip:** You earn 10 points for correctly predicting the winner, and 15 points for calling a Draw!")
