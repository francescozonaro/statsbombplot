import numpy as np
import os
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from tqdm import tqdm
from utils import (
    Pitch,
    getStatsbombAPI,
    addLegend,
    addNotes,
    saveFigure,
    fetchMatch,
)


class ShootingDistribution:
    def __init__(self, markerColor):
        self.markerColor = markerColor

    def draw(self, shotsCounts, starting_points, ending_points):

        pitch = Pitch()
        f, ax = pitch.draw()

        for i in range(ZONES_Y):
            for j in range(ZONES_X):
                count = shotsCounts[i, j]
                alphaFactor = 0.8 * count / np.max(shotsCounts)
                fill_rect = Rectangle(
                    (j * RECT_X, 80 - (i + 1) * RECT_Y),
                    RECT_X,
                    RECT_Y,
                    facecolor=self.markerColor,
                    alpha=alphaFactor,
                    edgecolor="none",
                    linewidth=0,
                    zorder=9,
                )
                edge_rect = Rectangle(
                    (j * RECT_X, 80 - (i + 1) * RECT_Y),
                    RECT_X,
                    RECT_Y,
                    edgecolor="#0c0c0c",
                    facecolor="none",
                    linewidth=0.3,
                    zorder=9,
                )

                ax.add_patch(fill_rect)
                ax.add_patch(edge_rect)

        for startPoint, endPoint in zip(starting_points, ending_points):
            ax.scatter(
                startPoint[0],
                startPoint[1],
                s=120,
                edgecolor="black",
                linewidth=0.6,
                facecolor=self.markerColor,
                zorder=5,
                marker="o",
                alpha=0.4,
            )
            ax.plot(
                [startPoint[0], endPoint[0]],
                [startPoint[1], endPoint[1]],
                linestyle="-",
                alpha=0.2,
                lw=0.6,
                zorder=5,
                color="#0c0c0c",
            )

        legendElements = [
            plt.scatter(
                [],
                [],
                s=70,
                edgecolor="black",
                linewidth=0.6,
                facecolor="#ffffff",
                zorder=5,
                marker="s",
                label="Few shots",
            ),
            plt.scatter(
                [],
                [],
                s=70,
                edgecolor="black",
                linewidth=0.6,
                facecolor=self.markerColor,
                zorder=5,
                marker="s",
                label="Many shots",
            ),
        ]

        return f, ax, legendElements


# Target keeper
playerName = "Federico Chiesa"
teamName = "Italy"
teamColor = "#1a759f"
load_360 = False

# Games
api = getStatsbombAPI()
df = api.games(competition_id=55, season_id=43)
df = df[df[["home_team_name", "away_team_name"]].isin([teamName]).any(axis=1)]
games = list(df["game_id"])
folder = os.path.join("imgs/", str(f"shootingDistribution"))
os.makedirs(folder, exist_ok=True)

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

shootingDistribution = ShootingDistribution(markerColor=teamColor)
fig, ax, legendElements = shootingDistribution.draw(
    shotCounts, startingPoints, endingPoints
)
extra = [f"{playerName} shooting distribution throughout EURO 2020"]
addLegend(ax, legendElements=legendElements)
addNotes(ax, extra_text=extra, author="@francescozonaro")
saveFigure(fig, f"{folder}/{playerName.lower().replace(' ', "")}Shooting.png")
