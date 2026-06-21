import requests
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class FootballAPI:
    BASE_URL = "https://api.football-data.org/v4"
    
    def __init__(self):
        self.headers = {
            "X-Auth-Token": st.secrets["football_data"]["API_TOKEN"]
        }

    def fetch_finished_matches(self, competition_code: str):
        """Fetches all finished matches for a specific league."""
        url = f"{self.BASE_URL}/competitions/{competition_code}/matches"
        params = {"status": "FINISHED"}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('matches', [])
        except Exception as e:
            logger.error(f"API Fetch Error: {e}")
            return []
