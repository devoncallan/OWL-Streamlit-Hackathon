import streamlit as st
from connection import BlizzardConnection
from os import path
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import numpy as np

@st.cache_data(ttl=3600)
def get_standings_df(_conn:BlizzardConnection, segment_id:str, region='west'):

    segment_data = _conn.get_segment_data(segment_id)
    standings_data = segment_data['standings']

    # Convert standings data to a DataFrame
    df = pd.DataFrame(standings_data)
    df = df.dropna(axis=1)

    # Extract region and rank
    def extract_division_info(row):
        division = row['divisions']
        region = list(division.keys())[0]
        rank   = division[region]['rank']
        return pd.Series([region, rank])
    
    df[['region', 'rank']] = df.apply(extract_division_info, axis=1)
    df.drop('divisions', axis=1, inplace=True)

    # Get teams in region
    df = df[df['region'] == region]

    team_ids = df['teamId'].values

    logos = []
    names = []
    for team_id in team_ids:
        
        team_data = _conn.get_team_data(team_id)
        logos.append(team_data['logo'])
        names.append(team_data['name'])
    logos_df = pd.DataFrame(logos, columns=['logo_url'])
    names_df = pd.DataFrame(names, columns=['name'])
    
    
    df = pd.concat([df, logos_df, names_df], axis=1)
    
    new_column_names = {
        'rank': '#',
        'logo_url': 'LOGO',
        'name': 'TEAM',
        'matchWins': 'W',
        'matchLosses': 'L',
        'gameDifferential': 'DIFF'
    }
    df.rename(columns=new_column_names, inplace=True)
    df['TEAM'] = df['TEAM'] + ' ' * 100
    print(df['TEAM'][0], 1)

    df['MP'] = df['W'] + df['L']
    df['WIN%'] = (df['W'] / df['MP']).map('{:.1%}'.format)
    df['MAP W-L-T'] = df['gameWins'].astype(str) + '-' + df['gameLosses'].astype(str) + '-' + df['gameTies'].astype(str)

    column_order = ['#', 'LOGO', 'TEAM', 'W', 'L', 'MP', 'MAP W-L-T', 'DIFF']
    df = df.reindex(columns=column_order)
    
    return df
    
def standings_board(_conn:BlizzardConnection, standings_df):

    team_ids = standings_df['teamId'].values

    logos = []
    names = []
    for team_id in team_ids:
        st.write(team_id)
        team_data = _conn.get_team_data(team_id)
        logos.append(team_data['logo'])
        names.append(team_data['name'])
    logos_df = pd.DataFrame(logos, columns=['logo_url'])
    names_df = pd.DataFrame(names, columns=['name'])
    # st.write(logos_df)
    standings_df = pd.concat([standings_df, logos_df, names_df], axis=1)
    return standings_df

    
