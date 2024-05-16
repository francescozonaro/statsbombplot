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

df_team = df_events[df_events["team_id"] == teams_id[0]].copy()
index_first_sub = df_team[df_team.type_name == "Substitution"].index.min()
df_events_pre_sub = df_team[df_team.index < index_first_sub]
df_passes = df_events_pre_sub[df_events_pre_sub.type_name == "Pass"]
df = df_passes[
    df_passes["extra"].apply(lambda x: "pass" in x and "outcome" in x["pass"]) == False
].reset_index(drop=True)
df["receiver"] = df["extra"].apply(
    lambda x: x.get("pass", {}).get("recipient", {}).get("name")
)
df["location_end"] = df["extra"].apply(lambda x: x.get("pass", {}).get("end_location"))

df[["player_name", "receiver"]] = df[["player_name", "receiver"]].replace(
    "Emerson Palmieri dos Santos", "Emerson Palmieri"
)
df[["player_name", "receiver"]] = df[["player_name", "receiver"]].replace(
    "Giovanni Di Lorenzo", "Giovanni DiLorenzo"
)
df[["player_name", "receiver"]] = df[["player_name", "receiver"]].replace(
    "Jorge Luiz Frello Filho", "Jorginho"
)

from statsbombplot.events import draw_passing_network

draw_passing_network(
    df, filename="ItalyPassingNetwork", marker_color=(0.5, 0.78, 0.97, 1)
)
