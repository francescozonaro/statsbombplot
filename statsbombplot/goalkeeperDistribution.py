import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from utils import (
    Pitch,
    getStatsbombAPI,
    addLegend,
    addNotes,
    saveFigure,
    fetchMatch,
)

api = getStatsbombAPI()
df = api.games(competition_id=55, season_id=43)
df = df[df[["home_team_name", "away_team_name"]].isin(["Italy"]).any(axis=1)]
games = list(df["game_id"])

playerName = "Gianluigi Donnarumma"
load_360 = True
folder = os.path.join(
    "imgs/", str(f"distribution_{playerName.lower().replace(' ', '_')}")
)
os.makedirs(folder, exist_ok=True)

pitch = Pitch()

ZONES_X = 6
ZONES_Y = 6
RECT_X = pitch.width / ZONES_X
RECT_Y = pitch.height / ZONES_Y
pass_counts = np.zeros((ZONES_Y, ZONES_X))

for gameId in games:
    match = fetchMatch(gameId, load_360)
    df = match.events
    passes = df[df["type_name"] == "Pass"]
    passes = passes[passes["player_name"] == playerName]

    for i, row in passes.iterrows():
        end_x = row["extra"]["pass"]["end_location"][0]
        end_y = 80 - row["extra"]["pass"]["end_location"][1]

        zone_x = int(end_x // RECT_X)
        zone_y = int(end_y // RECT_Y)

        if zone_x < ZONES_X and zone_y < ZONES_Y:
            pass_counts[zone_y, zone_x] += 1

f, ax = pitch.draw()
color = "#e76f51"

for i in range(ZONES_Y):
    for j in range(ZONES_X):
        count = pass_counts[i, j]
        alphaFactor = 0.8 * count / np.max(pass_counts)
        fill_rect = Rectangle(
            (j * RECT_X, 80 - (i + 1) * RECT_Y),
            RECT_X,
            RECT_Y,
            color=color,
            alpha=alphaFactor,
            edgecolor="none",  # No edge for the fill
            linewidth=0,
            zorder=8,
        )

        # Create the edge rectangle
        edge_rect = Rectangle(
            (j * RECT_X, 80 - (i + 1) * RECT_Y),
            RECT_X,
            RECT_Y,
            edgecolor="#0c0c0c",
            facecolor="none",
            linewidth=0.3,
            zorder=9,
        )

        # Add both patches to the axis
        ax.add_patch(fill_rect)
        ax.add_patch(edge_rect)


# Add a legend
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
        facecolor="#415a77",
        zorder=5,
        marker="s",
        label="Many passes",
    ),
]
extra = [f"{playerName} pass distribution"]
addLegend(ax, legendElements=legendElements)
addNotes(ax, extra_text=extra, author="@francescozonaro")
saveFigure(f, f"{folder}/keeperDistribution.png")
