# %%
import requests
import time
import pandas as pd
from itertools import product
import json

# %%
# Generate API KEY
response = requests.post('https://fbrapi.com/generate_api_key')
api_key = response.json()['api_key']
print("API Key:", api_key)

# %%
# Step 1: Get all countries 
url = "https://fbrapi.com/countries"
headers = {"X-API-Key": f"{api_key}"}

response = requests.get(url, headers=headers)
countries = response.json()
# print(countries)

# Step 2: Filter countries Top5 European Leagues
country_list = list()
for country in countries['data']:
    if country['country'].lower() in ['spain', 'germany', 'italy', 'england', 'france']:
        country_list.append([country['country'], country['country_code']])


# %%
# Step 3: Top5 European Leagues data as per Tier = 1st, Gender = M for Teams
url = "https://fbrapi.com/leagues"
headers = {"X-API-Key": f"{api_key}"}
domestic_leagues = list()

for country in country_list:
    params = {"country_code" : country[1]}
    response = requests.get(url, headers=headers, params=params)
    leagues = response.json()
    # print(type(leagues))
    
    for league in leagues.get('data', []):
        if league.get('league_type') == "domestic_leagues":
            for local_league in league.get('leagues', []):
                if local_league['tier']=='1st' and local_league['gender']=='M':
                    domestic_leagues.append([country[1],\
                                            local_league['competition_name'],\
                                            local_league['league_id'],\
                                            local_league['first_season'],\
                                            local_league['last_season']])
    time.sleep(10)
    
with open('domestic_leagues.json', 'w') as f:
    json.dump(domestic_leagues, f, indent=2)

# %%
# Step 4: Get Team IDs for Top5 European Leagues from last 15 seasons
url = "https://fbrapi.com/team-season-stats"
headers = {"X-API-Key": f"{api_key}"}

league_ids = [league[2] for league in domestic_leagues]
seasons = [str(i)+"-"+str(i+1) for i in range(2010,2025)]

teams_list_top_5 = list()  # Reset the list

for league, season in product(league_ids, seasons):
    params = {
        "league_id":league,
        "season_id":f"{season[0:4]}"
    }
    
    response = requests.get(url, headers=headers, params=params)
    season_teams_data = response.json()
    
    # Check if 'data' key exists in the response
    if 'data' in season_teams_data:
        print(f"Confirmation 'data' in league {league}, season {season}.")
        for teams in season_teams_data['data']:
            teams_list_top_5.append([teams['meta_data']['team_name'], teams['meta_data']['team_id']])
    else:
        print(f"Warning: No 'data' key for league {league}, season {season}. Response: {season_teams_data}")
    
    time.sleep(5)

teams_list_top_5_unique = sorted(list(set(tuple(team) for team in teams_list_top_5)))

with open("teams_list_top_5_unique.json", 'w') as f:
    json.dump(teams_list_top_5_unique, f, indent=2)

# %%
# Step 5: Define function to extract nested dictionaries
def extract_nested_dicts(input_dict):
    extracted_data = {}
    
    for key, value in input_dict.items():
        if isinstance(value, dict):
            nested_data = extract_nested_dicts(value)
            extracted_data.update(nested_data)
        else:
            extracted_data = {**extracted_data, **{key: value}}
            
    return extracted_data

# %%
# Step 6: Extract player seasonal data from Top5 European Leagues in the last 15 seasons
url = "https://fbrapi.com/player-season-stats"
headers = {"X-API-Key": f"{api_key}"}

league_ids = json.load(open('domestic_leagues.json'))
seasons = [str(i)+"-"+str(i+1) for i in range(2010,2025)]
teams_ids = json.load(open('teams_list_top_5_unique.json'))


for season in seasons:
    player_season_stats_flat = dict()    
    for league, team in product(league_ids, teams_ids):
        params = {
            "team_id" : team[1],
            "league_id" : league[2],
            "season_id" : season
            }
        response = requests.get(url, headers=headers, params=params)
        players_season_stats = response.json()
        
        for player in players_season_stats.get('players', []):
            player_dict = extract_nested_dicts(player)
            
            player_season_stats_flat.update({player['meta_data']['player_id']: player_dict})

    with open(f"players_season_stats_{season}.json", 'w') as f:
        json.dump(player_season_stats_flat, f, indent=2)

    time.sleep(6)


