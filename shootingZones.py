import matplotlib.pyplot as plt
import os
import numpy as np

from matplotlib.patches import Rectangle
from tqdm import tqdm
from utils import (
    getAllTeamMatchesFromSeason,
    getTeamsBySeason,
    fetchMatch,
    HalfPitch,
    saveFigure,
)

folder = os.path.join("imgs/", str(f"shootingDistribution"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

COMPETITION_ID = 2
SEASON_ID = 27
VIZ_COLOR = "#a41212"
NORMALIZE_PER_TEAM = True

teams = getTeamsBySeason(competitionId=COMPETITION_ID, seasonId=SEASON_ID)
teams = sorted(teams)

pitch_width = 60
pitch_height = 80
pitch_ratio = pitch_height / pitch_width

n_cols = 5
n_rows = 4

subplot_width = 4
fig_width = subplot_width * n_cols
fig_height = subplot_width * pitch_ratio * n_rows

fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_width, fig_height))
axes = axes.flatten()

maxShotCounts = 0
shotCountsMap = {}

for idx, team in enumerate(tqdm(teams, leave=False)):
    games = getAllTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)
    ZONES_X = 24
    ZONES_Y = 16
    RECT_X = 120 / ZONES_X
    RECT_Y = 80 / ZONES_Y
    shotCounts = np.zeros((ZONES_Y, ZONES_X))

    startingPoints = []
    endingPoints = []

    for gameId in tqdm(games, leave=False):
        match = fetchMatch(gameId, load_360=True)
        df = match.events
        shots = df[df["type_name"] == "Shot"]

        for i, shot in shots.iterrows():
            start_x = shot["location"][0]
            start_y = shot["location"][1]
            zone_x = int(start_x // RECT_X)
            zone_y = int(start_y // RECT_Y)

            startingPoints.append(shot["location"])
            endingPoints.append(shot["extra"]["shot"]["end_location"])
            if zone_x < ZONES_X and zone_y < ZONES_Y:
                shotCounts[zone_y, zone_x] += 1

    maxTeamShots = np.max(shotCounts)
    maxShotCounts = max(maxShotCounts, maxTeamShots)
    shotCountsMap[team] = shotCounts

for idx, team in enumerate(teams):

    pitch = HalfPitch()
    pitch.draw(ax=axes[idx])

    shotCounts = shotCountsMap[team]

    if NORMALIZE_PER_TEAM:
        maxShotCounts = np.max(shotCounts)

    for i in range(ZONES_Y):
        for j in range(ZONES_X):
            count = shotCounts[i, j]
            alphaFactor = 0.8 * count / maxShotCounts
            fill_rect = Rectangle(
                (j * RECT_X, 80 - (i + 1) * RECT_Y),
                RECT_X,
                RECT_Y,
                facecolor=VIZ_COLOR,
                alpha=alphaFactor,
                edgecolor="none",
                linewidth=0,
                zorder=9,
            )
            # edge_rect = Rectangle(
            #     (j * RECT_X, 80 - (i + 1) * RECT_Y),
            #     RECT_X,
            #     RECT_Y,
            #     edgecolor="#555555",
            #     facecolor="none",
            #     linewidth=0.1,
            #     linestyle=(0, (3, 3)),
            #     zorder=9,
            # )

            axes[idx].add_patch(fill_rect)
            # axes[idx].add_patch(edge_rect)

    axes[idx].text(59.5, 87, team, fontsize=10, va="center")


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
        facecolor=VIZ_COLOR,
        zorder=5,
        marker="s",
        label="Many shots",
    ),
]

fig.legend(
    handles=legendElements,
    loc="upper center",
    ncol=len(legendElements),
    bbox_to_anchor=(0.5, 0.93),
    fontsize=10,
    fancybox=True,
    frameon=False,
    handletextpad=0.5,
    handleheight=1.2,
)


saveFigure(
    fig,
    f"{folder}/testShootingDistribution.png",
)
