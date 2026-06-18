"""
Leaderboard computation and management
"""
import pandas as pd
import logging
from datetime import datetime, timezone
from src.config import Config
from src.storage import Storage

logger = logging.getLogger(__name__)


class LeaderboardManager:
    """Compute and manage leaderboards."""
    
    def __init__(self, config: Config, storage: Storage):
        self.config = config
        self.storage = storage
    
    def compute_leaderboard(self) -> pd.DataFrame:
        """
        Compute leaderboard from raw data.
        Aggregates user statistics and ranks.
        """
        # Read all necessary data
        users_df = pd.read_csv(self.config.USER_MASTER_PATH)
        predictions_df = pd.read_csv(self.config.PREDICTION_FACT_PATH)
        points_df = pd.read_csv(self.config.POINTS_FACT_PATH)
        
        leaderboard_data = []
        
        for _, user in users_df.iterrows():
            user_id = user['user_id']
            
            # Count predictions
            user_predictions = predictions_df[predictions_df['user_id'] == user_id]
            total_predictions = len(user_predictions)
            
            # Count correct predictions (where points > 0)
            user_points = points_df[points_df['user_id'] == user_id]
            correct_predictions = len(user_points[user_points['points'] > 0])
            
            # Calculate accuracy
            accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
            
            # Calculate total points
            total_points = int(user_points['points'].sum()) if not user_points.empty else 0
            
            leaderboard_data.append({
                'user_id': user_id,
                'user_name': user['user_name'],
                'total_predictions': total_predictions,
                'correct_predictions': correct_predictions,
                'accuracy_percentage': round(accuracy, 2),
                'total_points': total_points
            })
        
        # Create DataFrame and sort by total_points descending, then by accuracy
        leaderboard_df = pd.DataFrame(leaderboard_data)
        leaderboard_df = leaderboard_df.sort_values(
            by=['total_points', 'accuracy_percentage'],
            ascending=[False, False]
        ).reset_index(drop=True)
        
        # Add rank column
        leaderboard_df['rank'] = range(1, len(leaderboard_df) + 1)
        
        # Add timestamp
        leaderboard_df['last_updated'] = datetime.now(timezone.utc).strftime(self.config.DATETIME_FORMAT)
        
        # Reorder columns
        leaderboard_df = leaderboard_df[[
            'rank', 'user_id', 'user_name', 'total_predictions',
            'correct_predictions', 'accuracy_percentage', 'total_points', 'last_updated'
        ]]
        
        logger.info(f"Computed leaderboard with {len(leaderboard_df)} users")
        return leaderboard_df
    
    def compute_user_accuracy(self) -> pd.DataFrame:
        """Compute per-user accuracy metrics."""
        users_df = pd.read_csv(self.config.USER_MASTER_PATH)
        predictions_df = pd.read_csv(self.config.PREDICTION_FACT_PATH)
        results_df = pd.read_csv(self.config.MATCH_RESULT_PATH)
        
        accuracy_data = []
        
        for _, user in users_df.iterrows():
            user_id = user['user_id']
            user_predictions = predictions_df[predictions_df['user_id'] == user_id]
            
            total = len(user_predictions)
            if total == 0:
                continue
            
            correct = 0
            for _, pred in user_predictions.iterrows():
                result = results_df[results_df['match_id'] == pred['match_id']]
                if not result.empty:
                    if result.iloc[0]['actual_winner'] == pred['predicted_winner']:
                        correct += 1
            
            accuracy_percentage = (correct / total * 100) if total > 0 else 0
            
            accuracy_data.append({
                'user_id': user_id,
                'user_name': user['user_name'],
                'total_predictions': total,
                'correct_predictions': correct,
                'accuracy_percentage': round(accuracy_percentage, 2),
                'last_updated': datetime.now(timezone.utc).strftime(self.config.DATETIME_FORMAT)
            })
        
        accuracy_df = pd.DataFrame(accuracy_data)
        logger.info(f"Computed accuracy for {len(accuracy_df)} users")
        return accuracy_df
    
    def compute_tournament_stats(self) -> pd.DataFrame:
        """Compute tournament-level statistics."""
        matches_df = pd.read_csv(self.config.MATCH_MASTER_PATH)
        predictions_df = pd.read_csv(self.config.PREDICTION_FACT_PATH)
        results_df = pd.read_csv(self.config.MATCH_RESULT_PATH)
        users_df = pd.read_csv(self.config.USER_MASTER_PATH)
        
        stats = {
            'metric': [],
            'value': [],
            'last_updated': []
        }
        
        now = datetime.now(timezone.utc).strftime(self.config.DATETIME_FORMAT)
        
        # Total users
        stats['metric'].append('Total Users')
        stats['value'].append(str(len(users_df)))
        stats['last_updated'].append(now)
        
        # Total matches
        stats['metric'].append('Total Matches')
        stats['value'].append(str(len(matches_df)))
        stats['last_updated'].append(now)
        
        # Scheduled matches
        scheduled = len(matches_df[matches_df['status'] == 'scheduled'])
        stats['metric'].append('Scheduled Matches')
        stats['value'].append(str(scheduled))
        stats['last_updated'].append(now)
        
        # Completed matches
        completed = len(matches_df[matches_df['status'] == 'completed'])
        stats['metric'].append('Completed Matches')
        stats['value'].append(str(completed))
        stats['last_updated'].append(now)
        
        # Total predictions
        stats['metric'].append('Total Predictions')
        stats['value'].append(str(len(predictions_df)))
        stats['last_updated'].append(now)
        
        # Average predictions per user
        if len(users_df) > 0:
            avg_pred = len(predictions_df) / len(users_df)
            stats['metric'].append('Avg Predictions per User')
            stats['value'].append(f"{avg_pred:.2f}")
            stats['last_updated'].append(now)
        
        # Global accuracy
        if len(predictions_df) > 0:
            correct_preds = 0
            for _, pred in predictions_df.iterrows():
                result = results_df[results_df['match_id'] == pred['match_id']]
                if not result.empty:
                    if result.iloc[0]['actual_winner'] == pred['predicted_winner']:
                        correct_preds += 1
            
            global_accuracy = (correct_preds / len(predictions_df) * 100)
            stats['metric'].append('Global Accuracy')
            stats['value'].append(f"{global_accuracy:.2f}%")
            stats['last_updated'].append(now)
        
        return pd.DataFrame(stats)
    
    def refresh_all_gold_tables(self) -> None:
        """Refresh all gold layer tables."""
        logger.info("Starting gold layer refresh")
        
        leaderboard_df = self.compute_leaderboard()
        self.storage.save_leaderboard(leaderboard_df)
        
        accuracy_df = self.compute_user_accuracy()
        self.storage.save_user_accuracy(accuracy_df)
        
        stats_df = self.compute_tournament_stats()
        self.storage.save_tournament_stats(stats_df)
        
        logger.info("Gold layer refresh completed")
