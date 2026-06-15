import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid

# =====================================================

# CONFIG

# =====================================================

st.set_page_config(
page_title="FIFA World Cup 2026 Poll",
page_icon="⚽",
layout="wide"
)

FIXTURE_PATH = "data/FIFA2026_schedule_fixtures.csv"
VOTE_PATH = "data/votes.csv"

# =====================================================

# INITIALIZE

# =====================================================

Path("data").mkdir(exist_ok=True)

if not Path(VOTE_PATH).exists():
pd.DataFrame(
columns=[
"vote_id",
"match_number",
"date",
"team",
"username",
"timestamp",
]
).to_csv(VOTE_PATH, index=False)

# =====================================================

# LOAD FUNCTIONS

# =====================================================

@st.cache_data
def load_fixture():
df = pd.read_csv(FIXTURE_PATH)

```
df["date_dt"] = pd.to_datetime(
    df["date_dt"],
    format="%d-%m-%Y",
    errors="coerce",
)

return df
```

def load_votes():
return pd.read_csv(VOTE_PATH)

def save_vote(vote):

```
votes = load_votes()

votes = pd.concat(
    [votes, pd.DataFrame([vote])],
    ignore_index=True
)

votes.to_csv(
    VOTE_PATH,
    index=False
)

st.cache_data.clear()
```

# =====================================================

# LOAD DATA

# =====================================================

fixture = load_fixture()

today = pd.Timestamp.now().normalize()

today_matches = fixture[
fixture["date_dt"].dt.normalize()
== today
]

# =====================================================

# UI

# =====================================================

st.title("🏆 FIFA World Cup 2026 Match Poll")

username = st.text_input(
"Enter username"
)

if not username:
st.info("Enter a username to vote.")
st.stop()

# =====================================================

# NO MATCH TODAY

# =====================================================

if today_matches.empty:

```
st.success("No FIFA World Cup match scheduled today.")

upcoming = (
    fixture[
        fixture["date_dt"] > today
    ]
    .sort_values("date_dt")
    .head(10)
)

st.subheader("Upcoming Matches")

st.dataframe(
    upcoming[
        [
            "date_dt",
            "team 1",
            "team 2",
            "stadium",
        ]
    ]
)

st.stop()
```

# =====================================================

# MATCH POLLS

# =====================================================

votes = load_votes()

for _, match in today_matches.iterrows():

```
st.divider()

match_id = str(match["match_number"])

team1 = match["team 1"]
team2 = match["team 2"]

st.subheader(
    f"{team1} vs {team2}"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Group",
    match["group"]
)

col2.metric(
    "Stadium",
    match["stadium"]
)

col3.metric(
    "Match",
    match_id
)

already = votes[
    (votes["username"] == username)
    &
    (
        votes["match_number"]
        .astype(str)
        == match_id
    )
]

if already.empty:

    selection = st.radio(
        "Vote:",
        [
            team1,
            team2,
            "Draw"
        ],
        key=f"vote_{match_id}"
    )

    if st.button(
        "Submit Vote",
        key=f"submit_{match_id}"
    ):

        save_vote({

            "vote_id":
            str(uuid.uuid4()),

            "match_number":
            match_id,

            "date":
            str(today.date()),

            "team":
            selection,

            "username":
            username,

            "timestamp":
            datetime.utcnow()
        })

        st.success(
            "Vote recorded."
        )

        st.rerun()

else:

    st.warning(
        "You already voted."
    )

# RESULTS

current = load_votes()

current = current[
    current["match_number"]
    .astype(str)
    == match_id
]

if len(current):

    st.subheader(
        "Live Results"
    )

    results = (
        current["team"]
        .value_counts()
        .reset_index()
    )

    results.columns = [
        "Selection",
        "Votes"
    ]

    total = results["Votes"].sum()

    results["Percent"] = (
        results["Votes"]
        / total
        * 100
    ).round(2)

    st.dataframe(
        results,
        use_container_width=True
    )

    st.bar_chart(
        results.set_index(
            "Selection"
        )["Votes"]
    )
```

# =====================================================

# HISTORY

# =====================================================

st.divider()

st.subheader(
"Recent Votes"
)

history = load_votes()

if len(history):

```
st.dataframe(
    history.tail(50),
    use_container_width=True
)
```

else:

```
st.info(
    "No votes yet."
)
```
