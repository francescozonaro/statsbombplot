import random

from utils import getStatsbombAPI
from utils.commons import fetchMatch

matchesLength = 0
api = getStatsbombAPI()
df = api.competitions()
isValid = df["competition_name"] == "La Liga"

for row in df[isValid].itertuples():
    games = api.games(row.competition_id, row.season_id)
    for row in games.itertuples():
        print(len(fetchMatch(row.game_id).events))
    exit()
