"""
Background task scheduler
"""
import threading
import logging
import time
from datetime import datetime, timezone
from src.config import Config
from src.storage import Storage
from src.simulator import ResultSimulator
from src.leaderboard import LeaderboardManager

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """Background task scheduler for refresh operations."""
    
    def __init__(self, config: Config, storage: Storage):
        self.config = config
        self.storage = storage
        self.simulator = ResultSimulator(config, storage)
        self.leaderboard_mgr = LeaderboardManager(config, storage)
        
        self.running = False
        self.thread = None
    
    def start(self) -> None:
        """Start background scheduler."""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Background scheduler started")
    
    def stop(self) -> None:
        """Stop background scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Background scheduler stopped")
    
    def _run_scheduler(self) -> None:
        """Main scheduler loop."""
        result_check_interval = self.config.RESULT_REFRESH_INTERVAL_SECONDS
        leaderboard_check_interval = self.config.LEADERBOARD_REFRESH_INTERVAL_SECONDS
        
        last_result_check = 0
        last_leaderboard_check = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check for completed matches
                if current_time - last_result_check >= result_check_interval:
                    self._refresh_results()
                    last_result_check = current_time
                
                # Refresh leaderboard
                if current_time - last_leaderboard_check >= leaderboard_check_interval:
                    self._refresh_leaderboard()
                    last_leaderboard_check = current_time
                
                # Sleep to prevent busy waiting
                time.sleep(10)
            
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                time.sleep(30)
    
    def _refresh_results(self) -> None:
        """Refresh match results."""
        try:
            count = self.simulator.auto_simulate_completed_matches()
            if count > 0:
                logger.info(f"Refreshed {count} match results")
        except Exception as e:
            logger.error(f"Error refreshing results: {e}", exc_info=True)
    
    def _refresh_leaderboard(self) -> None:
        """Refresh leaderboard."""
        try:
            self.leaderboard_mgr.refresh_all_gold_tables()
            logger.info("Leaderboard refreshed")
        except Exception as e:
            logger.error(f"Error refreshing leaderboard: {e}", exc_info=True)


# Global scheduler instance
_scheduler = None


def initialize_scheduler(config: Config, storage: Storage) -> BackgroundScheduler:
    """Initialize the background scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(config, storage)
    return _scheduler


def start_background_tasks() -> None:
    """Start background scheduler tasks."""
    from src.config import Config
    from src.storage import Storage
    
    config = Config()
    storage = Storage(config)
    storage.initialize_data_layer()
    
    scheduler = initialize_scheduler(config, storage)
    scheduler.start()
