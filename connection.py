import streamlit as st
from streamlit.connections import ExperimentalBaseConnection
import requests
from requests.adapters import HTTPAdapter, Retry
from os import path
import time

# URLs for API and OAuth flow
API_URL      = 'https://{0}.api.blizzard.com/'
API_URL_CN   = 'https://gateway.battlenet.com.cn/'
OAUTH_URL    = 'https://oauth.battle.net/token'
OAUTH_URL_CN = 'https://oauth.battlenet.com.cn/token'

# Paths to data for API access
SUMMARY_DATA_PATH = 'owl/v1/owl2'
PLAYER_DATA_PATH  = 'owl/v1/players/{0}'
MATCH_DATA_PATH   = 'owl/v1/matches/{0}'
SEGMENT_DATA_PATH = 'owl/v1/segments/{0}'
TEAM_DATA_PATH    = 'owl/v1/teams/{0}'

class OWLConnection(ExperimentalBaseConnection[requests.Session]):

    def _connect(self, **kwargs) -> requests.Session:
        """
        Connects to Battle.net APIs, generates an access_token, and
        returns the requests session object.
        
        Returns:
            requests.Session: the requests session object.
        """
        if 'region' not in self._secrets: 
            self.oauth_url = OAUTH_URL.format('us')
            self.api_url = API_URL.format('us')
        elif self._secrets['region'] in ['us', 'eu', 'kr', 'tw']:
            self.oauth_url = OAUTH_URL.format(self._secrets['region'])
            self.api_url = API_URL.format(self._secrets['region'])
        elif self._secrets['region'] == 'cn':
            self.oauth_url = OAUTH_URL_CN
            self.api_URL = API_URL_CN
        else:
            raise Exception('Region in .streamlit/secrets.toml is not valid. Valid regions are us, eu, kr, tw, and cn.')

        client_id = self._secrets['client_id']
        client_secret = self._secrets['client_secret']
        query_params = {'grant_type': 'client_credentials'}

        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        
        response = session.post(
            url=self.oauth_url,
            params=query_params,
            auth=(client_id, client_secret)
        )
        self._access_token = response.json()['access_token']

        return session
    
    def cursor(self) -> requests.Session:
        """
        Returns the underlying requests session as the cursor.
        
        Returns:
            requests.Session: the requests session object.
        """
        if hasattr(self, '_instance') and self._instance:
            return self._instance
        
        self._instance = self._connect()
        return self._instance
    
    def get(self, url, ttl:int=3600, **kwargs) -> requests.Response:
        """
        Performs an HTTP get request
        
        Returns:
            requests.response: """

        @st.cache_data(ttl=ttl, **kwargs)
        def _get(url) -> dict:
            headers = {'Authorization': f'Bearer {self._access_token}'}
            cur = self.cursor()
            response = cur.get(url=url, headers=headers)
            return response

        response = _get(url)
        
        if response.status_code == 200:
            time.sleep(0.2)
            return response
        else:
            raise Exception(f'Failed to fetch data from {url} with error code {response.status_code}.')

    def get_summary_data(self) -> dict:
        """
        Returns a summary of OWL stats where you can get entity IDs (playerId, 
        matchId, segmentId, and teamId)

        Returns:
            dict: 
        """
        
        url = path.join(self.api_url, SUMMARY_DATA_PATH)
        summary_data = dict(self.get(url=url).json())
        return summary_data
    
    def get_player_data(self, player_id:str) -> dict:
        """
        Returns stats for a player
        
        Returns:
            dict: 
        """
        url = path.join(self.api_url, PLAYER_DATA_PATH)
        url = url.format(player_id)
        player_data = dict(self.get(url=url).json())
        return player_data
    
    def get_match_data(self, match_id:str) -> dict:
        """
        Returns stats for a match
        
        Returns:
            dict: 
        """

        url = path.join(self.api_url, MATCH_DATA_PATH)
        url = url.format(match_id)
        match_data = dict(self.get(url=url).json())
        return match_data
    
    def get_segment_data(self, segment_id:str):
        """
        Returns stats for a segment
        
        Returns:
            dict: 
        """

        url = path.join(self.api_url, SEGMENT_DATA_PATH)
        url = url.format(segment_id)
        segment_data = self.get(url=url).json()
        return segment_data

    def get_team_data(self, team_id:str) -> dict:
        """
        Returns stats for a team
        
        Returns:
            dict:
        """

        url = path.join(self.api_url, TEAM_DATA_PATH)
        url = url.format(team_id)
        team_data = dict(self.get(url=url).json())
        return team_data