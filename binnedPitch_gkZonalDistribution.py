import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import os
import numpy as np
import urllib.request

from PIL import Image
from math import ceil
from matplotlib.patches import Rectangle
from tqdm import tqdm
from utils import (
    getAllTeamMatchesFromSeason,
    getCompetitionTeamNames,
    fetchMatch,
    saveFigure,
    FullPitch,
)

folder = os.path.join("imgs/", str(f"goalkeeperDistribution"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

NORMALIZE_DATA = False
COMPETITION_ID = 2
SEASON_ID = 27
RECTANGLE_COLOR_HEX = "#7956a4"
EDGE_COLOR_HEX = "#535353"
FOTMOB_URL = "https://images.fotmob.com/image_resources/logo/teamlogo/"
TEAM_LOGO_URL = {
    "AFC Bournemouth": f"{FOTMOB_URL}8678.png",
    "Arsenal": f"{FOTMOB_URL}9825.png",
    "Aston Villa": f"{FOTMOB_URL}10252.png",
    "Chelsea": f"{FOTMOB_URL}8455.png",
    "Crystal Palace": f"{FOTMOB_URL}9826.png",
    "Everton": f"{FOTMOB_URL}8668.png",
    "Leicester City": f"{FOTMOB_URL}8197.png",
    "Liverpool": f"{FOTMOB_URL}8650.png",
    "Manchester City": f"{FOTMOB_URL}8456.png",
    "Manchester United": f"{FOTMOB_URL}10260.png",
    "Newcastle United": f"{FOTMOB_URL}10261.png",
    "Norwich City": f"{FOTMOB_URL}9850.png",
    "Southampton": f"{FOTMOB_URL}8466.png",
    "Stoke City": f"{FOTMOB_URL}10194.png",
    "Sunderland": f"{FOTMOB_URL}8472.png",
    "Swansea City": f"{FOTMOB_URL}10003.png",
    "Tottenham Hotspur": f"{FOTMOB_URL}8586.png",
    "Watford": f"{FOTMOB_URL}9817.png",
    "West Bromwich Albion": f"{FOTMOB_URL}8659.png",
    "West Ham United": f"{FOTMOB_URL}8654.png",
}

PITCH_WIDTH = 120
PITCH_HEIGHT = 80
PITCH_RATIO = PITCH_HEIGHT / PITCH_WIDTH
ZONES_X = 6
ZONES_Y = 5
RECT_X = 120 / ZONES_X
RECT_Y = 80 / ZONES_Y


def findPlayerNameByRole(df, team, role):
    startingXI = df[
        (df["type_name"] == "Starting XI") & (df["team_name"] == team)
    ].iloc[0]
    lineup = startingXI["extra"]["tactics"]["lineup"]
    candidate = next(player for player in lineup if player["position"]["name"] == role)
    return candidate["player"]["name"]


teams = sorted(
    getCompetitionTeamNames(competitionId=COMPETITION_ID, seasonId=SEASON_ID)
)[:20]

n_cols = min(len(teams), 5)
n_rows = int(ceil(len(teams) / n_cols))
subplot_width = 4
fig_width = subplot_width * n_cols
fig_height = subplot_width * n_rows * PITCH_RATIO
fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_width, fig_height))
axes = axes.flatten()

maxPassCounts = 0
passCountsMap = {}

for idx, team in enumerate(tqdm(teams, leave=False)):
    games = getAllTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)
    passCounts = np.zeros((ZONES_Y, ZONES_X))

    for gameId in tqdm(games, leave=False):
        match = fetchMatch(gameId, load_360=True)
        df = match.events

        PLAYER_NAME = findPlayerNameByRole(df, team, "Goalkeeper")

        isPass = df["type_name"] == "Pass"
        isTargetPlayer = df["player_name"] == PLAYER_NAME

        # Considering how Statsbomb data works, a pass is successful if there
        # is no "outcome" field in the extra dict.
        # Any outcome specification is negative (eg. Incomplete, Out, Unknown)
        isSuccessful = df["extra"].apply(
            lambda x: not (
                isinstance(x, dict) and "pass" in x and "outcome" in x["pass"]
            )
        )
        passes = df[isTargetPlayer & isPass & isSuccessful]

        for i, row in passes.iterrows():
            endX = row["extra"]["pass"]["end_location"][0]
            endY = 80 - row["extra"]["pass"]["end_location"][1]
            zoneX = int(endX // RECT_X)
            zoneY = int(endY // RECT_Y)
            if zoneX < ZONES_X and zoneY < ZONES_Y:
                passCounts[zoneY, zoneX] += 1

    maxTeamPasses = np.max(passCounts)
    maxPassCounts = max(maxPassCounts, maxTeamPasses)
    passCountsMap[team] = passCounts

for idx, team in enumerate(teams):
    pitch = FullPitch()
    pitch.draw(ax=axes[idx])
    passCounts = passCountsMap[team]

    if not NORMALIZE_DATA:
        maxPassCounts = np.max(passCounts)

    for i in range(ZONES_Y):
        for j in range(ZONES_X):
            count = passCounts[i, j]
            alphaFactor = 1 * count / maxPassCounts
            fill_rect = Rectangle(
                (j * RECT_X, 80 - (i + 1) * RECT_Y),
                RECT_X,
                RECT_Y,
                facecolor=RECTANGLE_COLOR_HEX,
                alpha=alphaFactor,
                edgecolor=EDGE_COLOR_HEX,
                linewidth=0.2,
                zorder=9,
            )
            axes[idx].add_patch(fill_rect)

            shareOfTeamPasses = passCounts / passCounts.sum()
            nonZeroShares = shareOfTeamPasses[shareOfTeamPasses > 0]
            thr = np.percentile(nonZeroShares, 95)
            shareOfZone = shareOfTeamPasses[i, j]
            if shareOfZone >= thr:
                axes[idx].text(
                    j * RECT_X + RECT_X / 2,
                    80 - (i + 1) * RECT_Y + RECT_Y / 2,
                    f"{shareOfZone*100:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="#ffffff",
                    zorder=10,
                    path_effects=[pe.withStroke(linewidth=0.5, foreground="black")],
                )

    img = Image.open(urllib.request.urlopen(TEAM_LOGO_URL[team])).convert("LA")
    image_ax = axes[idx].inset_axes(
        [0.02, 0.98, 0.10, 0.10], transform=axes[idx].transAxes
    )
    image_ax.imshow(img)
    image_ax.axis("off")

    axes[idx].text(13, 87, team, fontsize=10, va="center")

for i in range(len(teams), len(axes)):
    axes[i].axis("off")

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
        label="Few GK distributions",
    ),
    plt.scatter(
        [],
        [],
        s=70,
        edgecolor="black",
        linewidth=0.6,
        facecolor=RECTANGLE_COLOR_HEX,
        zorder=5,
        marker="s",
        label="Many GK distributions",
    ),
]

fig.legend(
    handles=legendElements,
    loc="upper center",
    ncol=len(legendElements),
    bbox_to_anchor=(0.5, 0.95),
    fontsize=10,
    fancybox=True,
    frameon=False,
    handletextpad=0.5,
    handleheight=2,
)

fig.text(
    0.82,
    0.05,
    "@francescozonaro",
    fontsize=12,
    ha="left",
    va="center",
    alpha=0.8,
)

fig.patch.set_facecolor("#f9f7f3")

saveFigure(
    fig,
    f"{folder}/goalkeeperZonalDistribution.png",
)
