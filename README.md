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
