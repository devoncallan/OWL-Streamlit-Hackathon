import streamlit as st
from connection import OWLConnection
import util

st.title('Overwatch League Data')
st.markdown('##### Author: Devon Callan')
st.markdown('###### Made for streamlit connections hackathon.')
st.divider()

# Set up connection to OWL API
conn = st.experimental_connection('OWL', type=OWLConnection)

# Initialize team data
util.initialize(conn)

# Get summary data from OWL api
summary = conn.get_summary_data()
segments = list(summary['segments'].keys())
segments = [segment for segment in segments if segment not in util.BLACKLIST_SEGMENTS]

# Select OWL season
st.header('Select data to visualize')
options=['2022', '2023']
selected_year = st.selectbox('Select a season.', options=options)
segments = [segment for segment in segments if selected_year in segment]

# Select OWL segment
selected_segment = st.selectbox('Select a current segment.', options=segments)

# Get the east and west standings for the selected segment
west_standings_df = util.get_standings_df(conn, segment_id=selected_segment, region='west')
east_standings_df = util.get_standings_df(conn, segment_id=selected_segment, region='east')

# Plot the standings dataframes
if west_standings_df is None and east_standings_df is None:
    st.error('No standings data for this segment.')
    st.stop()
if west_standings_df is not None:
    c = st.container()
    c.header('West')
    util.plot_standings_data(c, west_standings_df)
if east_standings_df is not None:
    c = st.container()
    c.header('East')
    util.plot_standings_data(c, east_standings_df)

# Get the team stats for the selected segment
team_stats_df = util.get_team_stats_df(conn, segment_id=selected_segment)

# Plot the team stats
c = st.container()
fig = util.plot_team_stats_data(c, team_stats_df)
st.pyplot(fig)