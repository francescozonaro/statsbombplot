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
types = ["Pass", "Carry"]
df = df_events[df_events["type_name"].isin(types)]
df = df[df["player_name"] == "Federico Chiesa"].reset_index(
    drop=True
)  # Consider only one player for the sake of tidiness

from statsbombplot.events import draw_progressive_events

draw_progressive_events(
    df,
    "Federico Chiesa",
    "chiesaProgressive",
    drawAttempted=False,
    toggleTimestamp=True,
)
