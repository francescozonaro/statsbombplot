import matplotlib.pyplot as plt
import os

from utils import (
    FullPitch,
    getStatsbombAPI,
    getAllTeamMatchesFromSeason,
    getCompetitionTeamNames,
)

folder = os.path.join("imgs/", str(f"shootingDistribution"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

COMPETITION_ID = 2
SEASON_ID = 27

uniqueTeamNames = getCompetitionTeamNames(
    competition_id=COMPETITION_ID, season_id=SEASON_ID
)
print(uniqueTeamNames)

for team in uniqueTeamNames:
    games = getAllTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)


exit()

ZONES_X = 6
ZONES_Y = 6
RECT_X = 120 / ZONES_X
RECT_Y = 80 / ZONES_Y
shotCounts = np.zeros((ZONES_Y, ZONES_X))

startingPoints = []
endingPoints = []

for gameId in tqdm(games, leave=False):
    match = fetchMatch(gameId, load_360)
    df = match.events
    shots = df[df["type_name"] == "Shot"]
    shots = shots[shots["player_name"] == playerName]

    for i, shot in shots.iterrows():
        start_x = shot["location"][0]
        start_y = shot["location"][1]
        zone_x = int(start_x // RECT_X)
        zone_y = int(start_y // RECT_Y)

        startingPoints.append(shot["location"])
        endingPoints.append(shot["extra"]["shot"]["end_location"])
        if zone_x < ZONES_X and zone_y < ZONES_Y:
            shotCounts[zone_y, zone_x] += 1
