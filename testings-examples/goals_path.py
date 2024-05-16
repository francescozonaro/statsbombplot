import os
import warnings
import sys
import socceraction.spadl as spadl
from statsbombpy.api_client import NoAuthWarning
from socceraction.data.statsbomb import StatsBombLoader

sys.path.append("..")
warnings.simplefilter("ignore", NoAuthWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
api = StatsBombLoader(getter="remote", creds={"user": "", "passwd": ""})

g = 3795506
df_teams = api.teams(game_id=g)
df_players = api.players(game_id=g)
df_events = api.events(game_id=g, load_360=True)
teams = list(df_events["team_name"].unique())
teams_id = list(df_events["team_id"].unique())
df_actions = spadl.statsbomb.convert_to_actions(df_events, home_team_id=teams_id[0])
df_actions = (
    spadl.add_names(df_actions)
    .merge(api.teams(game_id=g))
    .merge(api.players(game_id=g))
)
df_actions = df_actions.sort_values(
    by=["period_id", "time_seconds"], ascending=[True, True]
).reset_index(drop=True)

from statsbombplot.actions import draw_goals

draw_match_goals(df_actions)
