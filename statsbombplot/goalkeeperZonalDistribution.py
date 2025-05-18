import matplotlib.pyplot as plt
import os
import numpy as np

from math import ceil
from matplotlib.patches import Rectangle
from tqdm import tqdm
from utils import (
    getAllTeamMatchesFromSeason,
    getCompetitionTeamNames,
    fetchMatch,
    HalfPitch,
    FullPitch,
    saveFigure,
)


def findPlayerNameByRole(df, team, role):
    startingXI = df[
        (df["type_name"] == "Starting XI") & (df["team_name"] == team)
    ].iloc[0]
    lineup = startingXI["extra"]["tactics"]["lineup"]
    keeper = next(player for player in lineup if player["position"]["name"] == role)
    return keeper["player"]["name"]


folder = os.path.join("imgs/", str(f"goalkeeperDistribution"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

COMPETITION_ID = 2
SEASON_ID = 27
NORMALIZE_PER_TEAM = False
PLOT_SINGLE_TEAMS = False
TEAM_COLORS_HEX = {
    "AFC Bournemouth": "#db0007",
    "Arsenal": "#db0007",
    "Aston Villa": "#670e36",
    "Chelsea": "#034694",
    "Crystal Palace": "#db0007",
    "Everton": "#034694",
    "Leicester City": "#034694",
    "Liverpool": "#db0007",
    "Manchester City": "#6cabdd",
    "Manchester United": "#db0007",
    "Newcastle United": "#241f20",
    "Norwich City": "#8ac926",
    "Southampton": "#db0007",
    "Stoke City": "#db0007",
    "Sunderland": "#db0007",
    "Swansea City": "#241f20",
    "Tottenham Hotspur": "#241f20",
    "Watford": "#fdc500",
    "West Bromwich Albion": "#034694",
    "West Ham United": "#670e36",
}

PITCH_WIDTH = 120
PITCH_HEIGHT = 80
PITCH_RATIO = PITCH_HEIGHT / PITCH_WIDTH

teams = getCompetitionTeamNames(competitionId=COMPETITION_ID, seasonId=SEASON_ID)
teams = sorted(teams)
teams = teams[:18]
n_cols = min(len(teams), 5)
n_rows = int(ceil(len(teams) / n_cols))

subplot_width = 4
fig_width = subplot_width * n_cols
fig_height = subplot_width * PITCH_RATIO * n_rows

fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_width, fig_height))
axes = axes.flatten()

maxPassCounts = 0
passCountsMap = {}
startingPointsMap = {}
endingPointsMap = {}

for idx, team in enumerate(tqdm(teams, leave=False)):
    games = getAllTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)

    ZONES_X = 32
    ZONES_Y = 32
    RECT_X = 120 / ZONES_X
    RECT_Y = 80 / ZONES_Y
    passCounts = np.zeros((ZONES_Y, ZONES_X))
    startingPoints = []
    endingPoints = []

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
            startX = row["location"][0]
            startY = 80 - row["location"][1]
            endX = row["extra"]["pass"]["end_location"][0]
            endY = 80 - row["extra"]["pass"]["end_location"][1]
            zoneX = int(endX // RECT_X)
            zoneY = int(endY // RECT_Y)

            startingPoints.append(row["location"])
            endingPoints.append(row["extra"]["pass"]["end_location"])
            if zoneX < ZONES_X and zoneY < ZONES_Y:
                passCounts[zoneY, zoneX] += 1

    maxTeamPasses = np.max(passCounts)
    maxPassCounts = max(maxPassCounts, maxTeamPasses)
    passCountsMap[team] = passCounts
    startingPointsMap[team] = startingPoints
    endingPointsMap[team] = endingPoints

for idx, team in enumerate(teams):

    pitch = FullPitch()
    fSingle, axSingle = plt.subplots(1, 1, figsize=(15, 15 * (80 / 120)), dpi=300)
    pitch.draw(axSingle)
    pitch.draw(ax=axes[idx])

    passCounts = passCountsMap[team]

    if NORMALIZE_PER_TEAM:
        maxPassCounts = np.max(passCounts)

    for i in range(ZONES_Y):
        for j in range(ZONES_X):
            count = passCounts[i, j]
            alphaFactor = 1 * count / maxPassCounts
            fill_rect = Rectangle(
                (j * RECT_X, 80 - (i + 1) * RECT_Y),
                RECT_X,
                RECT_Y,
                facecolor=TEAM_COLORS_HEX[team],
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

            if PLOT_SINGLE_TEAMS:
                fill_rect_single = Rectangle(
                    (j * RECT_X, 80 - (i + 1) * RECT_Y),
                    RECT_X,
                    RECT_Y,
                    facecolor=TEAM_COLORS_HEX[team],
                    alpha=alphaFactor,
                    edgecolor="none",
                    linewidth=0,
                    zorder=9,
                )
                # edge_rect_single = Rectangle(
                #     (j * RECT_X, 80 - (i + 1) * RECT_Y),
                #     RECT_X,
                #     RECT_Y,
                #     edgecolor="#555555",
                #     facecolor="none",
                #     linewidth=0.1,
                #     linestyle=(0, (3, 3)),
                #     zorder=9,
                # )
                axSingle.add_patch(fill_rect_single)
                # axSingle.add_patch(edge_rect)

    for startPoint, endPoint in zip(startingPointsMap[team], endingPointsMap[team]):
        #     axes[idx].scatter(
        #         startPoint[0],
        #         startPoint[1],
        #         s=25,
        #         edgecolor="black",
        #         linewidth=0.6,
        #         facecolor=TEAM_COLORS_HEX[team],
        #         zorder=5,
        #         marker="o",
        #         alpha=0.4,
        #     )
        #     axes[idx].plot(
        #         [startPoint[0], endPoint[0]],
        #         [startPoint[1], endPoint[1]],
        #         linestyle="-",
        #         alpha=0.2,
        #         lw=0.6,
        #         zorder=5,
        #         color="#0c0c0c",
        #     )
        if PLOT_SINGLE_TEAMS:
            axSingle.scatter(
                startPoint[0],
                startPoint[1],
                s=25,
                edgecolor="black",
                linewidth=0.6,
                facecolor=TEAM_COLORS_HEX[team],
                zorder=5,
                marker="o",
                alpha=0.4,
            )
            axSingle.plot(
                [startPoint[0], endPoint[0]],
                [startPoint[1], endPoint[1]],
                linestyle="-",
                alpha=0.2,
                lw=0.6,
                zorder=5,
                color="#0c0c0c",
            )

    axes[idx].text(0, 87, team, fontsize=10, va="center")

    if PLOT_SINGLE_TEAMS:
        saveFigure(
            fSingle,
            f"{folder}/{team}.png",
        )

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
        label="Few shots",
    ),
    plt.scatter(
        [],
        [],
        s=70,
        edgecolor="black",
        linewidth=0.6,
        facecolor=TEAM_COLORS_HEX[team],
        zorder=5,
        marker="s",
        label="Many shots",
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
    f"{folder}/zFull.png",
)
