import streamlit as st
from connection import OWLConnection
import requests
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt

TEAM_DATA_LOADED_KEY = 'TEAM_DATA_LOADED'

BLACKLIST_SEGMENTS = [
    'owl2-2022-midseason-madness-tournament-qualifiers', 
    'owl2-2023-summer-knockouts',
    'owl2-2023-regular-tournaments',
    'owl2-2023-regular-tournaments-playoffs',
    'owl2-2023-post-season',
    'owl2-2023-spring-qualifiers-west',
    'owl2-2023-spring-qualifiers-east',
    'owl2-2023-spring-knockouts-west',
    'owl2-2023-spring-knockouts-east-1',
    'owl2-2023-spring-knockouts-east-2',
    'owl2-2023-summer-qualifiers-west',
    'owl2-2023-summer-qualifiers-east',
    'owl2-2023-summer-knockouts-east-1',
    'owl2-2023-summer-knockouts-east-2',
    'owl2-2023-midseason-madness-tournament-qualifiers',
    'owl2-2023-proam'
]

TEAM_STATS_COLUMN_NAMES = ['Damage Taken', 'Deaths', 'Eliminations', 'Final Blows', 'Healing Done', 'Hero Damage Done']
STANDINGS_WIDTH = [1.5, 1, 5, 1, 1, 2.5, 2.5, 2]
STANDINGS_TEXT_SIZE = '####'

FONT_SIZE = 20
FONT_FAMILY = 'Arial'
FONT_WEIGHT = 'Bold'
FORMAT_NORMAL = f'<p style="font-weight:{FONT_WEIGHT};              font-size: {FONT_SIZE}px; font-family:{FONT_FAMILY}">'
FORMAT_RED   = f'<p style="font-weight:{FONT_WEIGHT}; color:Red;   font-size: {FONT_SIZE}px; font-family:{FONT_FAMILY}">'
FORMAT_GREEN = f'<p style="font-weight:{FONT_WEIGHT}; color:Green; font-size: {FONT_SIZE}px; font-family:{FONT_FAMILY}">'

def initialize(_conn:OWLConnection):

    if TEAM_DATA_LOADED_KEY not in st.session_state:
        st.session_state[TEAM_DATA_LOADED_KEY] = False
    if not st.session_state[TEAM_DATA_LOADED_KEY]:
        load_team_data(_conn)

def load_team_data(_conn:OWLConnection):

    summary_data = _conn.get_summary_data()
    team_data = pd.DataFrame(summary_data['teams'])
    team_data = team_data.transpose()
    team_data.reset_index(inplace=True)
    loading_bar = st.progress(0, text='Loading team data. Please wait.')
    for index, team in team_data.iterrows():
        team_id = team['id']

        if team_id not in st.session_state:
            data = _conn.get_team_data(team_id=team_id)
            st.session_state[team_id] = data
            # Update progress bar
            current_percentage = index / (len(team_data))
            loading_bar.progress(current_percentage, text='Loading team data. Please wait.')
        
    st.session_state['TEAM_DATA_LOADED'] = True
    loading_bar.progress(100, text='All done!')

@st.cache_data(ttl=3600)
def get_standings_df(_conn:OWLConnection, segment_id:str, region='west'):

    segment_data = _conn.get_segment_data(segment_id)
    
    if 'standings' not in segment_data:
        return None
    standings_df = pd.DataFrame(segment_data['standings'])
    teams_df = pd.DataFrame(segment_data['teams'])

    standings_df.dropna(axis=1, inplace=True)
    teams_df.dropna(axis=1, inplace=True)

    

    # Return None if empty
    if standings_df.empty or teams_df.empty:
        return None
    
    

    # Extract region and rank
    def extract_division_info(row):
        division = row['divisions']
        region = list(division.keys())[0]
        rank   = division[region]['rank']
        return pd.Series([region, rank])
    
    standings_df[['region', 'rank']] = standings_df.apply(extract_division_info, axis=1)
    standings_df.drop('divisions', axis=1, inplace=True)

    # Get teams in region
    standings_df = standings_df[standings_df['region'] == region]

    # Add icons and names to standings_df
    icons = []
    names = []
    for team_id in standings_df['teamId']:
        team_data = st.session_state[team_id]
        icons.append(team_data['icon'])
        names.append(team_data['name'])
    icons_df = pd.DataFrame(icons, columns=['icon_url'])
    names_df = pd.DataFrame(names, columns=['name'])
    standings_df = pd.concat([standings_df, icons_df, names_df], axis=1)
    
    
    # Rename columns
    new_column_names = {
        'rank': '#',
        'icon_url': 'ICON',
        'name': 'TEAM',
        'matchWins': 'W',
        'matchLosses': 'L',
        'gameDifferential': 'DIFF'
    }
    
    standings_df.rename(columns=new_column_names, inplace=True)
    standings_df['TEAM'] = standings_df['TEAM'] + ' ' * 100
    
    # Add new columns
    standings_df['MP'] = standings_df['W'] + standings_df['L']
    standings_df[['gameWins', 'gameLosses', 'gameTies']] = standings_df[['gameWins', 'gameLosses', 'gameTies']].convert_dtypes(int)
    standings_df['WIN%'] = (standings_df['W'] / standings_df['MP']).map('{:.1%}'.format)
    standings_df['MAP W-L-T'] = standings_df['gameWins'].astype(str) + '-' + standings_df['gameLosses'].astype(str) + '-' + standings_df['gameTies'].astype(str)
    
    # Determine standings data columns
    column_order = ['#', 'ICON', 'TEAM', 'W', 'L', 'WIN%', 'MAP W-L-T', 'DIFF']
    standings_df = standings_df.reindex(columns=column_order)
    
    standings_df.dropna(axis=0, inplace=True)

    if standings_df.empty:
        return None
    
    return standings_df

def standings_header(c: st.container):

    rank_col, icon_col, team_name_col, win_col, loss_col, win_per_col, map_wlt_col, diff_col = c.columns(STANDINGS_WIDTH)
    rank_col.markdown(f"{STANDINGS_TEXT_SIZE} {'RANK'}")
    team_name_col.markdown(f"{STANDINGS_TEXT_SIZE} TEAM")
    win_col.markdown(f"{STANDINGS_TEXT_SIZE} W")
    loss_col.markdown(f"{STANDINGS_TEXT_SIZE} L")
    win_per_col.markdown(f"{STANDINGS_TEXT_SIZE} WIN%")
    map_wlt_col.markdown(f"{STANDINGS_TEXT_SIZE} MAP W-L-T")
    diff_col.markdown(f"{STANDINGS_TEXT_SIZE} DIFF")

def format_markdown(c: st.container, text, format:str=''):

    md = format + str(text) + '</p>'
    c.markdown(md, unsafe_allow_html=True)

def standings_card(c: st.container, standing_df):

    rank_col, icon_col, team_name_col, win_col, loss_col, win_per_col, map_wlt_col, diff_col = c.columns(STANDINGS_WIDTH)

    format_markdown(rank_col, int(standing_df['#']), FORMAT_NORMAL)
    icon_col.image(standing_df['ICON'], width=30)

    format_markdown(team_name_col, standing_df['TEAM'], FORMAT_NORMAL)
    format_markdown(win_col, int(standing_df['W']), FORMAT_NORMAL)
    format_markdown(loss_col, int(standing_df['L']), FORMAT_NORMAL)
    format_markdown(win_per_col, standing_df['WIN%'], FORMAT_NORMAL)
    format_markdown(map_wlt_col, standing_df['MAP W-L-T'], FORMAT_NORMAL)
    diff = int(standing_df['DIFF'])
    diff_str = str(diff)
    if diff > 0:
        diff_str = '+' + diff_str
        format_markdown(diff_col, diff_str, FORMAT_GREEN)
    else:
        format_markdown(diff_col, diff_str, FORMAT_RED)
    c.divider()
    return None

def plot_standings_data(c: st.container, standings_df:pd.DataFrame):

    standings_header(c)
    c.divider()
    for index, standing_df in standings_df.iterrows():
        c_sub = c.container()
        standings_card(c_sub, standing_df)
    return None

@st.cache_data(ttl=3600)    
def get_team_stats_df(_conn:OWLConnection, segment_id:str, region='west'):

    segment_data = _conn.get_segment_data(segment_id)
    teams_data = segment_data['teams']

    df = pd.DataFrame(teams_data)

    if df.empty:
        return None

    def extract_team_stats(row):
        team_stats = row['teamStats']
        damage_taken = team_stats['damageTaken']
        deaths = team_stats['deaths']
        eliminations = team_stats['eliminations']
        final_blows = team_stats['finalBlows']
        healing_done = team_stats['healingDone']
        hero_damage_done = team_stats['heroDamageDone']
        return pd.Series([damage_taken, deaths, eliminations, final_blows, healing_done, hero_damage_done])
    df[TEAM_STATS_COLUMN_NAMES] = df.apply(extract_team_stats, axis=1)
    df.drop('teamStats', axis=1, inplace=True)
    df.dropna(inplace=True)

    return df

def plot_team_stats_data(c:st.container, team_stats_df:pd.DataFrame):

    selected_data = c.selectbox('Select data to show', options=TEAM_STATS_COLUMN_NAMES)
    
    team_stats_df.sort_values(by=[selected_data], inplace=True)
    names = team_stats_df['name'].values
    data = team_stats_df[selected_data].values
    logo_urls = team_stats_df['logo'].values
    colors = '#' + team_stats_df['secondaryColor'].astype(str)

    labels = names
    values = data
    height = 0.8
    fig, ax = plt.subplots(dpi=300)
    plt.barh(y=labels, width=data, height=height, color=colors, align='center', edgecolor='black')

    plt.xlim(0, max(values) * 1.2)
    plt.ylim(-0.5, len(labels) - 0.5)
    y_axis_height = ax.get_ylim()[1] - ax.get_ylim()[0]
    x_axis_width = ax.get_xlim()[1] - ax.get_xlim()[0]
    axes_aspect_ratio = x_axis_width / y_axis_height
    img_offset = ax.get_xlim()[1] * 0.01

    for i, (label, value) in enumerate(zip(labels, values)):

        response = requests.get(logo_urls[i])
        img = plt.imread(BytesIO(response.content))
        img_height = height
        img_width  = axes_aspect_ratio * img_height
        aspect_ratio = img.shape[1] / img.shape[0]
        
        plt.imshow(img, extent=[value + img_offset, value + img_width + img_offset, i - img_height/2, i + img_height/2], aspect='auto', zorder=2)

    plt.tight_layout()
    title = 'Total ' + selected_data
    plt.title(title)
    plt.xlabel(selected_data)
    plt.yticks([])

    return fig