import matplotlib.patheffects as pe
import pandas as pd
from statsbombplot.utils import config, draw_pitch, change_range

def draw_passing_network(df_events, team_id):

    df_team = df_events[df_events['team_id'] == team_id].copy()
    index_first_sub = df_team[df_team.type_name == "Substitution"].index.min()
    df_events_pre_sub = df_team[df_team.index < index_first_sub]
    df_passes = df_events_pre_sub[df_events_pre_sub.type_name == "Pass"]
    df_received = df_passes[df_passes['extra'].apply(lambda x: 'pass' in x and 'outcome' in x['pass']) == False].reset_index(drop=True)
    df_received['receiver'] = df_received['extra'].apply(lambda x: x.get('pass', {}).get('recipient', {}).get('name'))
    df_received['location_end'] = df_received['extra'].apply(lambda x: x.get('pass', {}).get('end_location'))


    df = df_received.copy()

    df[['x', 'y']] = pd.DataFrame(df['location'].tolist())
    df[['x_end', 'y_end']] = pd.DataFrame(df['location_end'].tolist())

    df["x"] = df["x"].apply(lambda value: change_range(value, [0, max(df.x)], [0, 105]))
    df["y"] = df["y"].apply(lambda value: change_range(value, [0, max(df.y)], [0, 68]))
    df["x_end"] = df["x_end"].apply(lambda value: change_range(value, [0, max(df.x_end)], [0, 105]))
    df["y_end"] = df["y_end"].apply(lambda value: change_range(value, [0, max(df.y_end)], [0, 68]))

    df = df[['player_name', 'x', 'y', 'receiver', 'x_end', 'y_end']]

    player_pass_count = df.groupby('player_name').size().to_frame("num_passes")

    df['pair_key'] = df.apply(lambda x: "_".join(sorted([x['player_name'], x['receiver']])), axis = 1)
    pair_pass_count = df.groupby('pair_key').size().to_frame("num_passes")
    pair_pass_count = pair_pass_count[pair_pass_count['num_passes'] > 3]
    player_position = df.groupby('player_name').agg({"x" : "mean", "y" : "mean"})

    figsize_ratio = config['fig_size']/12
    ax = draw_pitch()

    max_player_count = player_pass_count.num_passes.max()
    max_pair_count = pair_pass_count.num_passes.max()

    for pair_key, row in pair_pass_count.iterrows():
        player1, player2 = pair_key.split("_")

        player1_x = player_position.loc[player1]['x']
        player1_y = player_position.loc[player1]['y']

        player2_x = player_position.loc[player2]['x']
        player2_y = player_position.loc[player2]['y']

        num_passes = row["num_passes"]

        line_width = num_passes/max_pair_count

        ax.plot([player1_x, player2_x], [player1_y, player2_y], linestyle='-', alpha = 0.4, lw = 2.5*line_width*figsize_ratio, zorder = 3, color = 'purple')


    for player_name, row in player_pass_count.iterrows():
        player_x = player_position.loc[player_name]['x']
        player_y = player_position.loc[player_name]['y']

        num_passes = row["num_passes"]

        marker_size = num_passes/max_player_count

        ax.plot(player_x, player_y, '.', markersize = 100*(marker_size)*figsize_ratio, color = 'purple', zorder=5)
        ax.plot(player_x, player_y, '.', markersize = 100*(marker_size)*figsize_ratio - 15*(marker_size)*figsize_ratio, color = 'white', zorder = 6)
        ax.annotate(player_name.split()[-1], xy=(player_x, player_y), ha='center', va='center', zorder=7, weight='bold', size = 8*figsize_ratio, path_effects=[pe.withStroke(linewidth = 2, foreground = 'white')])
