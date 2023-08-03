# OWL-Streamlit-Hackathon

Connect to the Battle.net [Overwatch League API](https://develop.battle.net/documentation/owl/community-apis) in a streamlit app using st.experimental_connection. Made for the Streamlit Connections Hackathon.

## Getting started

1. Follow this [Getting Started](https://develop.battle.net/documentation/guides/getting-started) guide to create a Battle.net client and generate a client secret.
2. Store the client credentials (client_id and client_secret) in .streamlit/secrets.toml (more information [here](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)). These will be exchanged for an access token through the OAuth client credentials flow.
3. (Optional) Store your region in .streamlit/secrets.toml. If not specified, the default region is us (more information [here](https://develop.battle.net/documentation/guides/regionality-and-apis))

`.streamlit/secrets.toml`
```
[connections.OWL]
region = 'us' # options: 'us', 'eu', 'kr', 'tw', and 'cn'
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
```

## Usage
1. Import
```python
import streamlit as st
from connection import OWLConnection
```

2. Initialize
```python
conn = st.experimental_connection('OWL', type=OWLConnection)
```

3. Query the [Overwatch League API](https://develop.battle.net/documentation/owl/community-apis) using helper functions:
   - `conn.get_summary_data()`
   - `conn.get_player_data(player_id)`
   - `conn.get_match_data(match_id)`
   - `conn.get_segment_data(segment_id)`
   - `conn.get_team_data(team_id)`

## Examples

#### Access summary data
```python
summary_data = conn.get_summary_data()
```

#### Access player data
```python
player_ids = list(summary_data['players'].keys())
player_id = player_ids[0]
player_data = conn.get_player_data(player_id)
```

#### Access match data
```python
match_ids = list(summary_data['matches'].keys())
match_id = match_ids[0]
match_data = conn.get_match_data(match_id)
```

#### Access segment data
```python
segment_ids = list(summary_data['segments'].keys())
segment_id = segment_ids[0]
segment_data = conn.get_segment_data(segment_id)
```

#### Access team data
```python
team_ids = list(summary_data['teams'].keys())
team_id = team_ids[0]
team_data = conn.get_team_data(team_id)
```
