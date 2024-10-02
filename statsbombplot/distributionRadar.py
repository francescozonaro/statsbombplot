import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patheffects as pe

from utils import (
    Pitch,
    getStatsbombAPI,
    addLegend,
    addNotes,
    saveFigure,
    fetchMatch,
)


# Helper functions
def calculate_pass_length(row):
    start_x, start_y = row.location
    end_x, end_y = row["extra"]["pass"]["end_location"]
    return np.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)


def calculate_pass_angle(x, y, end_x, end_y):
    dx, dy = end_x - x, end_y - y
    return np.arctan2(dy, dx)


# Setup
api = getStatsbombAPI()
df = api.games(competition_id=55, season_id=282)
df = df[df[["home_team_name", "away_team_name"]].isin(["France"]).any(axis=1)]
games = list(df["game_id"])

playerName = "Mike Maignan"
load_360 = True
folder = os.path.join(
    "imgs/", str(f"distribution_{playerName.lower().replace(' ', '_')}")
)
os.makedirs(folder, exist_ok=True)

# Arrays to store pass data
all_x = []
all_y = []

angles = []
pass_lengths = []
pass_counts = [0] * 8
pass_lengths_per_zone = [[] for _ in range(8)]

# Constants
NUM_ZONES = 8
MAX_ANGLE = np.pi

for gameId in games:
    match = fetchMatch(gameId, load_360)
    df = match.events
    passes = df[df["type_name"] == "Pass"]
    passes = passes[passes["player_name"] == playerName]

    for i, row in passes.iterrows():
        x = row.location[0]
        y = 80 - row.location[1]
        end_x = row["extra"]["pass"]["end_location"][0]
        end_y = 80 - row["extra"]["pass"]["end_location"][1]

        # Ignore passes behind goalkeeper's position
        if end_x < x:
            continue

        all_x.append(x)
        all_y.append(y)

avg_x = sum(all_x) / len(all_x) if all_x else None
avg_y = sum(all_y) / len(all_y) if all_y else None

plt.close()
pitch = Pitch()
f, ax = pitch.draw()

ax.plot(avg_x, avg_y, ".", markersize=100, color="#669bbc", zorder=5)
ax.plot(avg_x, avg_y, ".", markersize=85, color="white", zorder=6)

# Add a legend for the radar chart
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
extra = [f"Maignan radar distribution"]
addLegend(ax, legendElements=legendElements)
addNotes(ax, extra_text=extra, author="@francescozonaro")

# Save the figure
saveFigure(f, f"{folder}/radar.png")
