import os
import warnings
import sys
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

df_shots = df_events[
    (df_events["type_name"] == "Shot") & (df_events["period_id"] < 5)
].reset_index(drop=True)
df = api.games(competition_id=55, season_id=43)
df[(df["home_team_id"] == 914) | (df["away_team_id"] == 914)].game_id.unique()

from statsbombplot.events import draw_shotmap

draw_shotmap(df_shots, "shotmap", teams_id[0])
