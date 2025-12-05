#/zhome/f6/9/213532/CompToolsDSc_Project/CompTools_venv/bin/python3.11

import os
import soccerdata as sd
import pandas as pd
import warnings
import logging
# import sys

# output_folder = sys.argv[1] if len(sys.argv) >= 2 else os.getcwd() + '/data_output_23_24_extensive'
# star_season = int(sys.argv[2]) if len(sys.argv) > 2 else 23
# end_season = int(sys.argv[3]) if len(sys.argv) > 3 else 24

# Get Current Working Directory
output_folder = os.getcwd() + '/data_output'
start_season = 23
end_season = 24
# Suppress all warnings
warnings.filterwarnings("ignore")

# Suppress INFO logs from soccerdata
logging.getLogger('soccerdata').setLevel(logging.ERROR)

# Generate season list
season_list = [str(i)+'-'+str(i+1) for i in range(start_season, end_season)]
# Define the list of statistics to fetch
stat_list = ['standard', 'shooting', 'passing', 'passing_types', 'goal_shot_creation', 'defense', 'possession', 'playing_time', 'misc', 'keeper', 'keeper_adv']

for season in season_list:
    try:
        print(f"Processing season {season}...")
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            fbref = sd.FBref(leagues='Big 5 European Leagues Combined', seasons=season)
        player_season_stats = None
        keeper_season_stats = None
        
        # Fetch and combine stats for all stat types
        for stat in stat_list:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    # Fetch stats based on type
                    # Separate handling for keeper stats
                    if stat == 'keeper' or stat == 'keeper_adv':
                        # First time fetching keeper stats
                        if keeper_season_stats is None:
                            keeper_season_stats = fbref.read_player_season_stats(stat_type=stat)
                        # Subsequent merges for keeper stats
                        else:
                            stat_df = fbref.read_player_season_stats(stat_type=stat)
                            # Find distinct columns to avoid duplicates
                            distinct_columns = stat_df.columns.difference(keeper_season_stats.columns)
                            # Join only distinct columns
                            # Add rsuffix to avoid column name clashes
                            keeper_season_stats = keeper_season_stats.join(stat_df[distinct_columns], how='left', rsuffix='_drop')
                            
                            # Drop any duplicate columns that were added with the rsuffix
                            drop_cols = [col for col in keeper_season_stats.columns if col[0].endswith('_drop')]
                            if len(drop_cols) > 0:
                                print(f"Dropping duplicate columns from keeper stats: {drop_cols}")
                                keeper_season_stats.drop(columns=drop_cols, inplace=True)
                    
                    # Handling for non-keeper stats     
                    else:
                        # First time fetching player stats
                        if player_season_stats is None:
                            player_season_stats = fbref.read_player_season_stats(stat_type=stat)
                        # Subsequent merges for player stats
                        else:
                            stat_df = fbref.read_player_season_stats(stat_type=stat)
                            # Find distinct columns to avoid duplicates
                            distinct_columns = stat_df.columns.difference(player_season_stats.columns)
                            # Join only distinct columns
                            # Add rsuffix to avoid column name clashes
                            player_season_stats = player_season_stats.join(stat_df[distinct_columns], how='left', rsuffix='_drop')
                            
                            # Drop any duplicate columns that were added with the rsuffix
                            drop_cols = [col for col in player_season_stats.columns if col[0].endswith('_drop')]
                            if len(drop_cols) > 0:
                                print(f"Dropping duplicate columns from player stats: {drop_cols}")
                                player_season_stats.drop(columns=drop_cols, inplace=True)
            except Exception as e:
                print(f"Warning: Failed to fetch {stat} stats for {season}: {e}")
                continue
        
        # Check if data was successfully fetched
        if player_season_stats is None or player_season_stats.empty:
            print(f"Error: No player stats fetched for {season}, skipping...")
            continue
        
        if keeper_season_stats is None or keeper_season_stats.empty:
            print(f"Warning: No keeper stats fetched for {season}, skipping keeper file...")
            keeper_combined = None
        else:
            # Safely flatten columns if they are MultiIndex
            if isinstance(keeper_season_stats.columns, pd.MultiIndex):
                keeper_season_stats.columns = [' '.join(col[::-1]).strip(' ') for col in keeper_season_stats.columns]
            
            if isinstance(player_season_stats.columns, pd.MultiIndex):
                player_season_stats.columns = [' '.join(col[::-1]).strip(' ') for col in player_season_stats.columns]
            
            # Join player stats to keeper stats for only the same indexes in player_season_stats
            keeper_combined = keeper_season_stats.join(player_season_stats, how='left', rsuffix='_player')
        
        # Reset index to flatten MultiIndex rows
        player_season_stats.reset_index(inplace=True)
        
        # Save to CSV
        file_name = f'{output_folder}/player_season_stats_{season}.csv'
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Check if file exists and warn
        if os.path.exists(file_name):
            print(f"Warning: File {file_name} already exists and will be overwritten.")
            # remove the existing file
            os.remove(file_name)
            
        player_season_stats.to_csv(file_name, index=False)
        print(f"Saved player stats for {season}: {len(player_season_stats)} players")
        
        # Save keeper stats if available
        if keeper_combined is not None:
            keeper_combined.reset_index(inplace=True)
            # Save to CSV
            keeper_file_name = f'{output_folder}/keeper_season_stats_{season}.csv'
            # Check if file exists and warn
            if os.path.exists(keeper_file_name):
                print(f"Warning: File {keeper_file_name} already exists and will be overwritten.")
                # remove the existing file
                os.remove(keeper_file_name)
            # Save keeper stats
            keeper_combined.to_csv(keeper_file_name, index=False)
            print(f"Saved keeper stats for {season}: {len(keeper_combined)} keepers")
    
    except Exception as e:
        print(f"Error processing season {season}: {e}")
        continue
    
    # team_season_stats = fbref.read_team_season_stats(stat_type="standard", opponent_stats=False)
    # team_season_stats.to_csv(f'/zhome/f6/9/213532/CompToolsDSc_Project/data_output/team_season_stats_{season}.csv', index=True)