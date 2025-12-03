#/zhome/f6/9/213532/CompToolsDSc_Project/CompTools_venv/bin/python3.11

import soccerdata as sd

season_list = [str(i)+'-'+str(i+1) for i in range(10, 25)]
print(season_list)

for season in season_list:
    fbref = sd.FBref(leagues='Big 5 European Leagues Combined', seasons=season)
    
    # Read player season stats
    player_season_stats = fbref.read_player_season_stats(stat_type="standard")
    
    # Get column names from level 0 of MultiIndex for first 4 columns
    cols_level_0 = player_season_stats.columns.droplevel([1]).to_list()[:4]
    
    # Reset index to flatten MultiIndex rows
    player_season_stats.reset_index(inplace=True,col_level=1)
    
    # Get column names from level 1 of MultiIndex for remaining columns
    cols_level_1 = player_season_stats.columns.droplevel([0]).values.tolist()

    # Add suffix " per 90min" to last 10 columns to differentiate per 90min stats
    columns_90min = [f"{col} per 90min" for col in cols_level_1[-10:]]

    # Combine all column names
    column_names = cols_level_1[:4]+cols_level_0+cols_level_1[8:-10]+columns_90min
    # Assign new column names to DataFrame
    player_season_stats.columns = column_names
    
    # Save to CSV
    player_season_stats.to_csv(f'/zhome/f6/9/213532/CompToolsDSc_Project/data_output/player_season_stats_{season}.csv', index=False)
    
    # team_season_stats = fbref.read_team_season_stats(stat_type="standard", opponent_stats=False)
    # team_season_stats.to_csv(f'/zhome/f6/9/213532/CompToolsDSc_Project/data_output/team_season_stats_{season}.csv', index=True)