import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid

st.set_page_config(
page_title="FIFA World Cup Poll",
page_icon="⚽"
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FIXTURE = "data/FIFA2026_schedule_fixtures.csv"
VOTES = "data/votes.csv"

# create votes file

if not Path(VOTES).exists():
df = pd.DataFrame(
columns=[
"vote_id",
"match_number",
"username",
"prediction",
"timestamp"
]
)

```
df.to_csv(
    VOTES,
    index=False
)
```

@st.cache_data
def load_fixture():

```
df = pd.read_csv(FIXTURE)

df["date_dt"] = pd.to_datetime(
    df["date_dt"],
    format="%d-%m-%Y",
    errors="coerce"
)

return df
```

def load_votes():

```
return pd.read_csv(VOTES)
```

def save_vote(data):

```
votes = load_votes()

votes.loc[len(votes)] = data

votes.to_csv(
    VOTES,
    index=False
)
```

st.title(
"🏆 FIFA World Cup 2026 Poll"
)

user = st.text_input(
"Enter username"
)

if user == "":
st.stop()

fixture = load_fixture()

today = pd.Timestamp.today().normalize()

matches = fixture[
fixture["date_dt"].dt.normalize()
== today
]

if matches.empty:

```
st.info(
    "No match today"
)
```

else:

```
votes = load_votes()

for _, match in matches.iterrows():

    match_id = str(
        match["match_number"]
    )

    t1 = match["team 1"]
    t2 = match["team 2"]

    st.subheader(
        f"{t1} vs {t2}"
    )

    previous = votes[
        (
            votes["username"]
            == user
        )
        &
        (
            votes[
                "match_number"
            ].astype(str)
            == match_id
        )
    ]

    if previous.empty:

        choice = st.radio(
            "Predict winner",
            [
                t1,
                t2,
                "Draw"
            ],
            key=match_id
        )

        if st.button(
            "Submit",
            key=match_id
        ):

            save_vote([

                str(
                    uuid.uuid4()
                ),

                match_id,

                user,

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

        st.bar_chart(
            result[
                "prediction"
            ].value_counts()
        )
```
