import streamlit as st
from connection import BlizzardConnection
import pandas as pd
from util import get_standings_df

st.title('Overwatch League Standings')
conn = st.experimental_connection('blizzard', type=BlizzardConnection)

summary = conn.get_summary_data()
current_segments = summary['currentSegments']

segment_data = conn.get_segment_data(segment_id='owl2-2023-midseason-madness-tournament-qualifiers')


df = get_standings_df(conn, segment_id='owl2-2023-midseason-madness-tournament-qualifiers')

st.dataframe(
    df,
    column_config={
        "LOGO": st.column_config.ImageColumn(
            "LOGO"
        )
    },
    hide_index=True,
    use_container_width=False,
    height = 35*(len(df)+1)+3
)