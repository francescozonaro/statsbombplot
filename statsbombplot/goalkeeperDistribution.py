import numpy as np
import os
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


class GoalkeeperDistribution:
    def __init__(self, markerColor):
        self.markerColor = markerColor

    def draw(self, pass_counts, starting_points, ending_points):

        pitch = Pitch()
        f, ax = pitch.draw()

        for i in range(ZONES_Y):
            for j in range(ZONES_X):
                count = pass_counts[i, j]
                alphaFactor = 0.8 * count / np.max(pass_counts)
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
                    alpha=0.4
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
                label="Few passes",
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
                label="Many passes",
            ),
        ]

        return f, ax, legendElements


playerName = "Gianluigi Donnarumma"
teamName = "Italy"
teamColor = "#1a759f"
load_360 = True


api = getStatsbombAPI()
df = api.games(competition_id=55, season_id=43)
df = df[df[["home_team_name", "away_team_name"]].isin([teamName]).any(axis=1)]
games = list(df["game_id"])
folder = os.path.join(
    "imgs/", str(f"goalkeeperDistribution")
)
os.makedirs(folder, exist_ok=True)

ZONES_X = 6
ZONES_Y = 6
RECT_X = 120 / ZONES_X
RECT_Y = 80 / ZONES_Y
pass_counts = np.zeros((ZONES_Y, ZONES_X))

startingPoints = []
endingPoints = []

for gameId in tqdm(games, leave=False):
    match = fetchMatch(gameId, load_360)
    df = match.events
    passes = df[df["type_name"] == "Pass"]
    passes = passes[passes["player_name"] == playerName]
    passes = passes[passes['extra'].apply(lambda x: x['pass']['outcome'] if isinstance(x, dict) and 'pass' in x and 'outcome' in x['pass'] else None).isna()]

    for i, row in passes.iterrows():
        start_x = row['location'][0]
        start_y = row['location'][1]
        end_x = row["extra"]["pass"]["end_location"][0]
        end_y = 80 - row["extra"]["pass"]["end_location"][1]
        zone_x = int(end_x // RECT_X)
        zone_y = int(end_y // RECT_Y)

        startingPoints.append(row["location"])   
        endingPoints.append(row["extra"]["pass"]["end_location"])        

        if zone_x < ZONES_X and zone_y < ZONES_Y:
            pass_counts[zone_y, zone_x] += 1

goalkeeperDistribution = GoalkeeperDistribution(markerColor=teamColor)
fig, ax, legendElements = goalkeeperDistribution.draw(pass_counts, startingPoints, endingPoints)
extra = [f"{playerName} pass distribution throughout EURO 2020"]
addLegend(ax, legendElements=legendElements)
addNotes(ax, extra_text=extra, author="@francescozonaro")
saveFigure(fig, f"{folder}/{playerName.lower().replace(' ', "")}Distribution.png")
