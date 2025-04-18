import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from tqdm import tqdm
from utils import (
    Pitch,
    addLegend,
    addNotes,
    saveFigure,
    fetchMatch,
    getAllTeamMatchesFromSeason,
    normalizeString,
)

folder = os.path.join("imgs/", str(f"goalkeeperZonalDistribution"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"


# PLAYER_NAME = "Jordan Pickford"
# TEAM_NAME = "England"
# MARKER_COLOR = "#f0150f"
# COMPETITION_ID = 55
# SEASON_ID = 43

# PLAYER_NAME = "Gianluigi Donnarumma"
# TEAM_NAME = "Italy"
# MARKER_COLOR = "#1f759f"
# COMPETITION_ID = 55
# SEASON_ID = 43

PLAYER_NAME = "Claudio Andrés Bravo Muñoz"
TEAM_NAME = "Barcelona"
MARKER_COLOR = "#1f759f"
COMPETITION_ID = 11
SEASON_ID = 27

games = getAllTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, TEAM_NAME)

ZONES_X = 4
ZONES_Y = 4
RECT_X = 120 / ZONES_X
RECT_Y = 80 / ZONES_Y
passCounts = np.zeros((ZONES_Y, ZONES_X))
startingPoints = []
endingPoints = []

for gameId in tqdm(games, leave=False):
    match = fetchMatch(gameId, load_360=True)
    df = match.events
    isPass = df["type_name"] == "Pass"
    isTargetPlayer = df["player_name"] == PLAYER_NAME
    # Considering how Statsbomb data works, a pass is successful if there iss not "outcome" field in the extra dict
    # Any outcome specification is negative (eg. Incomplete, Out, Unknown)
    isSuccessful = df["extra"].apply(
        lambda x: not (isinstance(x, dict) and "pass" in x and "outcome" in x["pass"])
    )
    passes = df[isTargetPlayer & isPass & isSuccessful]

    for i, row in passes.iterrows():
        startX = row["location"][0]
        startY = row["location"][1]
        endX = row["extra"]["pass"]["end_location"][0]
        endY = 80 - row["extra"]["pass"]["end_location"][1]
        zoneX = int(endX // RECT_X)
        zoneY = int(endY // RECT_Y)

        startingPoints.append(row["location"])
        endingPoints.append(row["extra"]["pass"]["end_location"])
        if zoneX < ZONES_X and zoneY < ZONES_Y:
            passCounts[zoneY, zoneX] += 1

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
            linestyle=(0, (3, 3, 1, 3)),
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
        label="Low pass volume",
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
        label="High pass volume",
    ),
]

extra = [f"{PLAYER_NAME} zonal pass distribution"]
addLegend(ax, legendElements=legendElements)
addNotes(ax, extra_text=extra, author="@francescozonaro")
saveFigure(
    f,
    f"{folder}/{normalizeString(PLAYER_NAME).replace(' ', '')}ZonalDistribution.png",
)
