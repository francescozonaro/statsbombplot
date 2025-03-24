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

#
# PLAYER_NAME = "Jordan Pickford"
# TEAM_NAME = "England"
# MARKER_COLOR = "#f0150f"
# PLAYER_NAME = "Gianluigi Donnarumma"
# TEAM_NAME = "Italy"
# MARKER_COLOR = "#1f759f"
# COMPETITION_ID = 55
# SEASON_ID = 43

PLAYER_NAME = "Claudio Andrés Bravo Muñoz"
TEAM_NAME = "Barcelona"
MARKER_COLOR = "#1f759f"
COMPETITION_ID = 11  # 55
SEASON_ID = 27  # 43
#


LOAD_360 = True
api = getStatsbombAPI()
df = api.games(competition_id=COMPETITION_ID, season_id=SEASON_ID)
df = df[df[["home_team_name", "away_team_name"]].isin([TEAM_NAME]).any(axis=1)]
games = list(df["game_id"])
folder = os.path.join("imgs/", str(f"goalkeeperDistribution"))
os.makedirs(folder, exist_ok=True)

#
ZONES_X = 10
ZONES_Y = 10
RECT_X = 120 / ZONES_X
RECT_Y = 80 / ZONES_Y
passCounts = np.zeros((ZONES_Y, ZONES_X))
startingPoints = []
endingPoints = []

for gameId in tqdm(games, leave=False):
    match = fetchMatch(gameId, LOAD_360)
    df = match.events
    passes = df[df["type_name"] == "Pass"]
    passes = passes[passes["player_name"] == PLAYER_NAME]
    passes = passes[
        passes["extra"]
        .apply(
            lambda x: (
                x["pass"]["outcome"]
                if isinstance(x, dict) and "pass" in x and "outcome" in x["pass"]
                else None
            )
        )
        .isna()
    ]

    for i, row in passes.iterrows():
        start_x = row["location"][0]
        start_y = row["location"][1]
        end_x = row["extra"]["pass"]["end_location"][0]
        end_y = 80 - row["extra"]["pass"]["end_location"][1]
        zone_x = int(end_x // RECT_X)
        zone_y = int(end_y // RECT_Y)

        startingPoints.append(row["location"])
        endingPoints.append(row["extra"]["pass"]["end_location"])
        if zone_x < ZONES_X and zone_y < ZONES_Y:
            passCounts[zone_y, zone_x] += 1

pitch = Pitch()
f, ax = pitch.draw()

for i in range(ZONES_Y):
    for j in range(ZONES_X):
        zonePasses = passCounts[i, j]
        alphaFactor = 0.9 * zonePasses / np.max(passCounts)
        fill_rect = Rectangle(
            (j * RECT_X, 80 - (i + 1) * RECT_Y),
            RECT_X,
            RECT_Y,
            facecolor=MARKER_COLOR,
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

for startPoint, endPoint in zip(startingPoints, endingPoints):
    ax.scatter(
        startPoint[0],
        startPoint[1],
        s=120,
        edgecolor="black",
        linewidth=0.6,
        facecolor=MARKER_COLOR,
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
        label="Few passes",
    ),
    plt.scatter(
        [],
        [],
        s=70,
        edgecolor="black",
        linewidth=0.6,
        facecolor=MARKER_COLOR,
        zorder=5,
        marker="s",
        label="Many passes",
    ),
]

extra = [f"{PLAYER_NAME} pass distribution throughout EURO 2020"]
addLegend(ax, legendElements=legendElements)
addNotes(ax, extra_text=extra, author="@francescozonaro")
saveFigure(f, f"{folder}/{PLAYER_NAME.lower().replace(' ', "")}Distribution.png")
