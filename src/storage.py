def sync_results_from_api(self, competition_code: str):
        """Fetches results from football-data.org and updates the database."""
        from src.api import FootballAPI
        api = FootballAPI()
        matches = api.fetch_finished_matches(competition_code)
        
        count = 0
        for match in matches:
            # 1. Prepare Match ID
            match_id = str(match['id'])
            
            # 2. Determine winner from API format
            # API returns 'HOME_TEAM', 'AWAY_TEAM', or 'DRAW'
            score_info = match.get('score', {})
            winner_key = score_info.get('winner')
            
            if winner_key == 'HOME_TEAM':
                winner_name = match['homeTeam']['name']
            elif winner_key == 'AWAY_TEAM':
                winner_name = match['awayTeam']['name']
            else:
                winner_name = 'draw'
            
            # 3. Check if result already exists to avoid duplicate entries
            existing = self.get_match_result(match_id)
            if not existing:
                self.save_match_result(match_id, winner_name)
                self.update_match_status(match_id, 'completed')
                count += 1
        
        logger.info(f"Synced {count} new results from API")
