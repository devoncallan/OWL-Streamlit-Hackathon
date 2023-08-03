import streamlit as st
from streamlit.connections import ExperimentalBaseConnection
import requests
from os import path
import time

class BlizzardConnection(ExperimentalBaseConnection[requests.Session]):

    def _connect(self, **kwargs) -> requests.Session:
        """
        Connects to Battle.net APIs, generates an access_token, and
        returns the requests session object.
        
        Returns:
            requests.Session: the requests session object.
        """
        oauth_url = self._secrets['oauth_url']
        client_id = self._secrets['client_id']
        client_secret = self._secrets['client_secret']
        query_params = {'grant_type': 'client_credentials'}

        session = requests.Session()
        
        response = session.post(
            url=oauth_url,
            params=query_params,
            auth=(client_id, client_secret)
        )
        self._access_token = response.json()['access_token']
        st.write(self._access_token)

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
            time.sleep(0.05)
            return response
        elif response.status_code == 429:
            # st.write(response.json())
            # print(response.json())
            raise Exception(f'Failed to fetch data from {url} with error code {response.status_code}.') 
        else:
            raise Exception(f'Failed to fetch data from {url} with error code {response.status_code}.')
        # num_retries = 3
        # for i in range(num_retries):

        #     response = _get(url)
        #     if response.status_code == 200:
        #         return response
        #     elif response.status_code == 427:
        #         time.sleep(1)
        #     else:
        #         print(response.status_code)
        #         raise Exception(f'Failed to fetch data from {url}.')
        # raise Exception(f'Failed to fetch data from {url}.')
        # response = _get(url)
        
        # # If the GET request is successful, the status_code will be 200
        # if response.status_code == 200:
        #     time.sleep(0.1)
        #     return response
        # if response.status_code == 427:
        #     time.sleep(1)
        # else:
        #     print(response.status_code)
        #     raise Exception(f'Failed to fetch data from {url}.')

    def get_summary_data(self) -> dict:
        """
        Returns a summary of OWL stats where you can get entity IDs (playerId, 
        matchId, segmentId, and teamId)

        Returns:
            dict: 
        """
        
        url = path.join(self._secrets['api_url'], self._secrets['paths']['summary_data'])
        # summary_response = self.get(url=url, ttl=ttl)
        summary_data = dict(self.get(url=url).json())
        return summary_data
    
    def get_player_data(self, player_id:str) -> dict:
        """
        Returns stats for a player
        
        Returns:
            dict: 
        """
        url = path.join(self._secrets['api_url'], self._secrets['paths']['player_data'])
        url = url.format(player_id)
        player_data = dict(self.get(url=url).json())
        return player_data
    
    def get_match_data(self, match_id:str) -> dict:
        """
        Returns stats for a match
        
        Returns:
            dict: 
        """

        url = path.join(self._secrets['api_url'], self._secrets['paths']['match_data'])
        url = url.format(match_id)
        match_data = dict(self.get(url=url).json())
        return match_data
    
    def get_segment_data(self, segment_id:str):
        """
        Returns stats for a segment
        
        Returns:
            dict: 
        """

        url = path.join(self._secrets['api_url'], self._secrets['paths']['segment_data'])
        url = url.format(segment_id)
        segment_data = self.get(url=url).json()
        return segment_data

    def get_team_data(self, team_id:str) -> dict:
        """
        Returns stats for a team
        
        Returns:
            dict:
        """

        url = path.join(self._secrets['api_url'], self._secrets['paths']['team_data'])
        url = url.format(team_id)
        team_data = dict(self.get(url=url).json())
        return team_data