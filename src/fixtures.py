"""
Fixture loading and validation
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from src.config import Config

logger = logging.getLogger(__name__)


class FixtureLoader:
    """Load and validate tournament fixtures."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def load_from_csv(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """
        Load fixtures from CSV file.
        
        Expected columns:
        - team_1: First team name
        - team_2: Second team name
        - stage: Tournament stage (Group, Round of 16, etc.)
        - match_date: Match date (YYYY-MM-DD)
        - kickoff_time: Kickoff time (HH:MM:SS)
        - venue: Match venue
        """
        path = file_path or self.config.FIXTURES_PATH
        
        if not path.exists():
            logger.warning(f"Fixtures file not found: {path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(path)
            logger.info(f"Loaded {len(df)} fixtures from {path}")
            return df
        except Exception as e:
            logger.error(f"Error loading fixtures: {e}")
            return pd.DataFrame()
    
    def validate_fixtures(self, df: pd.DataFrame) -> bool:
        """Validate fixture data."""
        required_columns = ['team_1', 'team_2', 'stage', 'match_date', 'kickoff_time', 'venue']
        
        if df.empty:
            logger.warning("Fixtures DataFrame is empty")
            return False
        
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Missing required column: {col}")
                return False
        
        # Validate dates
        try:
            pd.to_datetime(df['match_date'], format='%Y-%m-%d')
        except Exception as e:
            logger.error(f"Invalid date format: {e}")
            return False
        
        logger.info("Fixture validation successful")
        return True
    
    def ensure_fixtures_loaded(self, storage) -> bool:
        """Load fixtures if not already loaded."""
        matches = storage.get_all_matches()
        
        if len(matches) > 0:
            logger.info(f"Fixtures already loaded ({len(matches)} matches)")
            return True
        
        fixtures_df = self.load_from_csv()
        
        if fixtures_df.empty:
            logger.warning("No fixtures available")
            return False
        
        if not self.validate_fixtures(fixtures_df):
            logger.error("Fixture validation failed")
            return False
        
        storage.load_fixtures(fixtures_df)
        return True


def create_sample_fixtures() -> pd.DataFrame:
    """
    Create sample fixtures for testing.
    Replace with actual FIFA 2026 schedule.
    """
    data = {
        'team_1': [
            'USA', 'Mexico', 'Canada', 'Argentina',
            'Brazil', 'France', 'Germany', 'Spain',
            'England', 'Netherlands', 'Belgium', 'Italy',
            'Japan', 'South Korea', 'Australia', 'Saudi Arabia',
            'USA', 'Argentina', 'Brazil', 'France'
        ],
        'team_2': [
            'Mexico', 'Canada', 'USA', 'Uruguay',
            'Paraguay', 'Uruguay', 'France', 'Germany',
            'France', 'Germany', 'Spain', 'Netherlands',
            'Germany', 'Japan', 'Saudi Arabia', 'Australia',
            'Brazil', 'France', 'Germany', 'England'
        ],
        'stage': [
            'Group', 'Group', 'Group', 'Group',
            'Group', 'Group', 'Group', 'Group',
            'Group', 'Group', 'Group', 'Group',
            'Group', 'Group', 'Group', 'Group',
            'Round of 16', 'Round of 16', 'Quarterfinals', 'Quarterfinals'
        ],
        'match_date': [
            '2026-06-12', '2026-06-12', '2026-06-13', '2026-06-13',
            '2026-06-14', '2026-06-14', '2026-06-15', '2026-06-15',
            '2026-06-16', '2026-06-16', '2026-06-17', '2026-06-17',
            '2026-06-18', '2026-06-18', '2026-06-19', '2026-06-19',
            '2026-07-02', '2026-07-02', '2026-07-10', '2026-07-10'
        ],
        'kickoff_time': [
            '16:00:00', '20:00:00', '13:00:00', '16:00:00',
            '20:00:00', '16:00:00', '13:00:00', '20:00:00',
            '16:00:00', '20:00:00', '13:00:00', '16:00:00',
            '20:00:00', '16:00:00', '13:00:00', '20:00:00',
            '16:00:00', '20:00:00', '16:00:00', '20:00:00'
        ],
        'venue': [
            'Arlington', 'Mexico City', 'Toronto', 'Buenos Aires',
            'Brasília', 'Paris', 'Berlin', 'Madrid',
            'London', 'Amsterdam', 'Brussels', 'Rome',
            'Tokyo', 'Seoul', 'Sydney', 'Riyadh',
            'Los Angeles', 'Chicago', 'Miami', 'New York'
        ]
    }
    
    return pd.DataFrame(data)
