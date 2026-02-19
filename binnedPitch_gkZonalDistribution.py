import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import os
import numpy as np
import urllib.request

from PIL import Image
from matplotlib.patches import Rectangle
from tqdm import tqdm
from utils import *

folder = os.path.join("imgs/", str(f"goalkeeperDistribution"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = FONT_FAMILY

COMPETITION_ID = 2
SEASON_ID = 27
ZONES_X = 6
ZONES_Y = 5
ZONE_WIDTH = PITCH_WIDTH / ZONES_X
ZONE_HEIGHT = PITCH_HEIGHT / ZONES_Y
NORMALIZE_GLOBALLY = False
VIZ_NAME = f"gkDistribution_{COMPETITION_ID}_{SEASON_ID}"


def findPlayerNameByRole(df, team, role):
    startingXI = df[
        (df["type_name"] == "Starting XI") & (df["team_name"] == team)
    ].iloc[0]
    lineup = startingXI["extra"]["tactics"]["lineup"]
    candidate = next(player for player in lineup if player["position"]["name"] == role)
    return candidate["player"]["name"]


# Data processing
teams = sorted(getTeamsBySeason(competitionId=COMPETITION_ID, seasonId=SEASON_ID))
maxPassCounts = 0
passCountsMap = {}

for idx, team in enumerate(tqdm(teams, leave=False)):
    games = getAllTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)
    pass_counts = np.zeros((ZONES_Y, ZONES_X))

    for gameId in tqdm(games, leave=False):
        match = fetchMatch(gameId, load_360=True)
        df = match.events
        player_name = findPlayerNameByRole(df, team, "Goalkeeper")

        # Considering Statsbomb data, a pass is successful if there is no "outcome" in the extra dict. Any outcome specification is negative (eg. Incomplete, Out, Unknown)
        is_pass = df["type_name"] == "Pass"
        is_target_player = df["player_name"] == player_name
        passes = df[is_target_player & is_pass]
        passes = passes[passes["extra"].apply(lambda x: "outcome" not in x["pass"])]

        # Vectorized extraction of end locations and zone assignment
        end_locations = passes["extra"].apply(lambda x: x["pass"]["end_location"])
        end_x = np.array([loc[0] for loc in end_locations])
        end_y = 80 - np.array([loc[1] for loc in end_locations])
        pass_counts += count_in_pitch_zones(
            end_x, end_y, ZONES_X, ZONES_Y, PITCH_WIDTH, PITCH_HEIGHT
        )

    maxTeamPasses = np.max(pass_counts)
    maxPassCounts = max(maxPassCounts, maxTeamPasses)
    passCountsMap[team] = pass_counts


# Drawing
fig, axes = make_matplotlib_grid(
    len(teams), max_cols=5, subplot_width=4, ratio=PITCH_RATIO
)
for idx, team in enumerate(teams):
    pitch = FullPitch()
    pitch.draw(ax=axes[idx])
    pass_counts = passCountsMap[team]

    if not NORMALIZE_GLOBALLY:
        maxPassCounts = np.max(pass_counts)

    shareOfTeamPasses = pass_counts / pass_counts.sum()
    nonZeroShares = shareOfTeamPasses[shareOfTeamPasses > 0]
    thr = np.percentile(nonZeroShares, 95)
    for i in range(ZONES_Y):
        for j in range(ZONES_X):
            count = pass_counts[i, j]
            alphaFactor = 1 * count / maxPassCounts
            fill_rect = Rectangle(
                (j * ZONE_WIDTH, 80 - (i + 1) * ZONE_HEIGHT),
                ZONE_WIDTH,
                ZONE_HEIGHT,
                facecolor=PURPLE_HEX,
                alpha=alphaFactor,
                edgecolor=GRAY_HEX,
                linewidth=0.2,
                zorder=9,
            )
            axes[idx].add_patch(fill_rect)

            shareOfZone = shareOfTeamPasses[i, j]
            if shareOfZone >= thr:
                axes[idx].text(
                    j * ZONE_WIDTH + ZONE_WIDTH / 2,
                    80 - (i + 1) * ZONE_HEIGHT + ZONE_HEIGHT / 2,
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

legendElements = [
    plt.scatter(
        [],
        [],
        s=70,
        edgecolor=PLAIN_BLACK_HEX,
        linewidth=0.6,
        facecolor=PLAIN_WHITE_HEX,
        zorder=5,
        marker="s",
        label="Few GK distributions",
    ),
    plt.scatter(
        [],
        [],
        s=70,
        edgecolor=PLAIN_BLACK_HEX,
        linewidth=0.6,
        facecolor=PURPLE_HEX,
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
    WATERMARK,
    fontsize=12,
    ha="left",
    va="center",
    alpha=0.8,
)

fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)

saveFigure(
    fig,
    f"{folder}/{VIZ_NAME}.png",
)
