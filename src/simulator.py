"""
Match result simulator for testing and demo purposes
"""
import random
import logging
from datetime import datetime, timezone, timedelta
from typing import Tuple
from src.config import Config
from src.storage import Storage
import pandas as pd

logger = logging.getLogger(__name__)


class ResultSimulator:
    """Simulate match results."""
    
    def __init__(self, config: Config, storage: Storage):
        self.config = config
        self.storage = storage
    
    def simulate_match_result(self, match_id: str) -> Tuple[str, str]:
        """
        Simulate a match result.
        Returns (actual_winner, result_string)
        """
        match = self.storage.get_match(match_id)
        if not match:
            return None, "Match not found"
        
        # Check if already has result
        if self.storage.has_result(match_id):
            result = self.storage.get_match_result(match_id)
            return result['actual_winner'], "Already has result"
        
        # Randomly decide outcome
        # 40% team1, 40% team2, 20% draw
        rand = random.random()
        
        if rand < 0.40:
            winner = match['team_1']
            result_str = f"{match['team_1']} won"
        elif rand < 0.80:
            winner = match['team_2']
            result_str = f"{match['team_2']} won"
        else:
            winner = 'draw'
            result_str = "Draw"
        
        return winner, result_str
    
    def process_match_results(self, match_id: str) -> Tuple[bool, str]:
        """
        Simulate and save match result.
        Process points for all predictions.
        """
        match = self.storage.get_match(match_id)
        if not match:
            return False, "Match not found"
        
        if self.storage.has_result(match_id):
            return False, "Match already has a result"
        
        # Simulate result
        winner, result_str = self.simulate_match_result(match_id)
        
        # Save result
        self.storage.save_match_result(match_id, winner)
        
        # Update match status
        self.storage.update_match_status(match_id, 'completed')
        
        # Process points for all predictions
        from src.predictions import PredictionManager
        pred_manager = PredictionManager(self.config, self.storage)
        pred_manager.process_match_results(match_id, winner)
        
        logger.info(f"Processed results for match {match_id}: {result_str}")
        return True, result_str
    
    def auto_simulate_completed_matches(self) -> int:
        """
        Automatically simulate results for matches that should be completed.
        Returns number of matches processed.
        """
        matches = self.storage.get_matches_by_status('scheduled')
        now = datetime.now(timezone.utc)
        
        processed_count = 0
        
        for match in matches:
            # Parse match time
            match_datetime_str = f"{match['match_date']} {match['kickoff_time']}"
            match_datetime = datetime.strptime(match_datetime_str, "%Y-%m-%d %H:%M:%S")
            match_datetime = match_datetime.replace(tzinfo=timezone.utc)
            
            # Check if match should be completed (45 minutes after kickoff for demo)
            completion_time = match_datetime + timedelta(minutes=45)
            
            if now >= completion_time and not self.storage.has_result(match['match_id']):
                success, msg = self.process_match_results(match['match_id'])
                if success:
                    processed_count += 1
        
        logger.info(f"Auto-simulated {processed_count} matches")
        return processed_count
    
    def bulk_simulate_all_results(self) -> int:
        """Simulate results for all scheduled matches (for admin testing)."""
        matches = self.storage.get_matches_by_status('scheduled')
        processed_count = 0
        
        for match in matches:
            success, _ = self.process_match_results(match['match_id'])
            if success:
                processed_count += 1
        
        logger.info(f"Bulk simulated {processed_count} matches")
        return processed_count
