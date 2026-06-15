import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid

st.set_page_config(
page_title="FIFA World Cup Poll",
page_icon="⚽",
layout="wide"
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FIXTURE_FILE = "data/FIFA2026_schedule_fixtures.csv"
VOTES_FILE = "data/votes.csv"

# Create votes file automatically

try:
pd.read_csv(VOTES_FILE)

except:

```
pd.DataFrame(
    columns=[
        "vote_id",
        "match_number",
        "username",
        "prediction",
        "timestamp"
    ]
).to_csv(
    VOTES_FILE,
    index=False
)
```

@st.cache_data
def load_fixture():

```
df = pd.read_csv(FIXTURE_FILE)

df["date_dt"] = pd.to_datetime(
    df["date_dt"],
    format="%d-%m-%Y",
    errors="coerce"
)

return df
```

def load_votes():

```
return pd.read_csv(
    VOTES_FILE
)
```

def save_vote(record):

```
votes = load_votes()

votes.loc[
    len(votes)
] = record

votes.to_csv(
    VOTES_FILE,
    index=False
)
```

st.title(
"🏆 FIFA World Cup 2026 Poll"
)

username = st.text_input(
"Username"
)

if username == "":
st.stop()

fixtures = load_fixture()

today = pd.Timestamp.today().normalize()

today_games = fixtures[
fixtures["date_dt"].dt.normalize()
== today
]

if len(today_games) == 0:

```
st.info(
    "No matches today."
)

st.stop()
```

votes = load_votes()

for _, game in today_games.iterrows():

```
match_id = str(
    game["match_number"]
)

team1 = game["team 1"]
team2 = game["team 2"]

st.subheader(
    f"{team1} vs {team2}"
)

already = votes[
    (
        votes["username"]
        == username
    )
    &
    (
        votes[
            "match_number"
        ].astype(str)
        == match_id
    )
]

if len(already) == 0:

    choice = st.radio(
        "Prediction",
        [
            team1,
            team2,
            "Draw"
        ],
        key=match_id
    )

    if st.button(
        "Vote",
        key=match_id
    ):

        save_vote([

            str(
                uuid.uuid4()
            ),

            match_id,

            username,

            choice,

            str(
                datetime.now()
            )

        ])

        st.success(
            "Vote saved"
        )

        st.rerun()

else:

    st.warning(
        "Already voted"
    )

result = load_votes()

result = result[
    result[
        "match_number"
    ].astype(str)
    == match_id
]

if len(result):

    chart = (
        result[
            "prediction"
        ]
        .value_counts()
    )

    st.bar_chart(
        chart
    )
```
