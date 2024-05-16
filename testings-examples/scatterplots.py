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
draw_id = 0

# Group the events to plot. Remember: Everything is plotted with the same marker. In this example we are plotting defensive actions.
types = [
    "Block",
    "Interception",
    "Clearance",
    "Ball Recovery",
]
df = df_events[df_events["type_name"].isin(types)]

# Decide the team to plot
df = df[df["team_id"] == teams_id[draw_id]].reset_index(drop=True)

# Sometimes it may be useful to ignore the keeper
df = df[df["position_name"] != "Goalkeeper"]

# We consider only situations where the opponent has the ball
df = df[df["possession_team_id"] == teams_id[abs(draw_id - 1)]]

from statsbombplot.events import draw_event_type_scatter

draw_event_type_scatter(
    df,
    filename=f"defAction{teams[draw_id].split()[0]}",
    event_type=f"{teams[draw_id]} Def. Action",
    marker_shape="p",
    marker_color=(0.5, 0.78, 0.97, 1),
)
