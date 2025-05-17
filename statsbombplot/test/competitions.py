from utils import getStatsbombAPI
import random

matchesLength = 0

while matchesLength < 370:
    api = getStatsbombAPI()
    competitions = api.competitions()
    randomRow = competitions.sample(n=1, random_state=random.randint(0, 10000)).iloc[0]
    games = api.games(randomRow.competition_id, randomRow.season_id)
    matchesLength = len(games)
    if matchesLength > 370:
        print(
            f"{randomRow.competition_name} - {randomRow.competition_id} | {randomRow.season_name} - {randomRow.season_id} | {len(games)}",
        )
