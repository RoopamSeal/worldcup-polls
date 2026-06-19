# FIFA World Cup 2026 Predictor ⚽

A production-grade Streamlit application for predicting FIFA World Cup 2026 match outcomes, tracking predictions, and competing on a global leaderboard.

## Features

- **User Authentication**: Simple username-based registration and login
- **Match Predictions**: Predict match outcomes before kickoff
- **Real-time Leaderboard**: Track your ranking against other players
- **Prediction History**: View all your predictions with accuracy metrics
- **Tournament Statistics**: Monitor tournament progress and key stats
- **Admin Console**: Manage fixtures, simulate results, and refresh data
- **CSV Lakehouse Architecture**: Fully local, no external dependencies
- **Scheduled Tasks**: Automatic hourly refresh of results and leaderboards

## Architecture

### Data Layer (CSV Lakehouse)

**Silver Layer** (Raw Transactional Data):
- `user_master.csv`: User registration data
- `match_master.csv`: Match fixtures and schedule
- `prediction_fact.csv`: User predictions
- `match_result.csv`: Actual match results

**Gold Layer** (Analytics & Aggregations):
- `leaderboard.csv`: Ranked user statistics
- `user_accuracy.csv`: User accuracy metrics
- `tournament_stats.csv`: Tournament-level statistics

### Backend Architecture
src/

├── config.py           # Configuration management

├── storage.py          # CSV I/O and data operations

├── fixtures.py         # Fixture loading and validation

├── predictions.py      # Prediction logic and scoring

├── leaderboard.py      # Leaderboard computation

├── simulator.py        # Match result simulation

└── scheduler.py        # Background task orchestration

### Frontend (Streamlit Pages)

- **01_Home.py**: Tournament dashboard and statistics
- **02_Predict.py**: Make predictions on active matches
- **03_My_Predictions.py**: View prediction history and accuracy
- **04_Leaderboard.py**: Global ranking and filters
- **05_Admin.py**: Admin console for data management

## Installation

### Prerequisites
- Python 3.9+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/worldcup-predictor.git
cd worldcup-predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Deploy with one click

## Data Model

### user_master
user_id          | UUID/int

user_name        | string (unique)

email            | string (optional)

country          | string

registration_date| datetime

status           | string (active/inactive)

### match_master

match_id         | UUID/int

team_1           | string

team_2           | string

stage            | string (group/knockout)

match_date       | date

kickoff_time     | time

venue            | string

status           | string (scheduled/live/completed)

### prediction_fact

prediction_id    | UUID/int

user_id          | foreign key

match_id         | foreign key

predicted_winner | string (team_1/team_2/draw)

prediction_timestamp | datetime


### match_result

match_id         | foreign key

actual_winner    | string (team_1/team_2/draw)

result_timestamp | datetime

### points_fact
user_id          | foreign key

match_id         | foreign key

points           | int (0/2/3)

processed_timestamp | datetime

### leaderboard
rank             | int

user_id          | foreign key

user_name        | string

total_predictions| int

correct_predictions | int

accuracy_percentage | float

total_points     | int

last_updated     | datetime


## Scoring System

| Outcome | Points |
|---------|--------|
| Correct Winner | +3 |
| Correct Draw | +2 |
| Wrong Prediction | 0 |

## Rules

1. **Prediction Window**: Predictions must be submitted before match kickoff
2. **Auto-Registration**: Users are automatically registered on first login
3. **Result Source**: Match results are simulated automatically after scheduled kickoff time
4. **Leaderboard**: Updated hourly via background scheduler
5. **Accuracy**: Calculated as (correct_predictions / total_predictions) * 100

