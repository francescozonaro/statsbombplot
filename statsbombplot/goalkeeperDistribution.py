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

ZONES_X = 12
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
cmap = plt.get_cmap("Reds")
for i in range(ZONES_Y):
    for j in range(ZONES_X):
        count = pass_counts[i, j]
        color = cmap(count / np.max(pass_counts) if np.max(pass_counts) > 0 else 1)
        rect = Rectangle(
            (j * RECT_X, 80 - (i + 1) * RECT_Y),
            RECT_X,
            RECT_Y,
            color=color,
            alpha=0.6,
            edgecolor="black",
        )
        ax.add_patch(rect)

# Add a legend
legendElements = [
    plt.scatter(
        [],
        [],
        s=70,
        edgecolor="black",
        linewidth=0.6,
        facecolor="#669bbc",
        zorder=5,
        marker="o",
        label=playerName,
    ),
]
extra = [f"{playerName} pass distribution"]
addLegend(ax, legendElements=legendElements)
addNotes(ax, extra_text=extra, author="@francescozonaro")
saveFigure(f, f"{folder}/keeperDistribution.png")
