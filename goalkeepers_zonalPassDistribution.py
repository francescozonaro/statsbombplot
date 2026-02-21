import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import os
import numpy as np
import urllib.request

from PIL import Image
from matplotlib.patches import Rectangle
from tqdm import tqdm

from utils.commons import (
    count_in_pitch_zones,
    fetchMatch,
    getTeamMatchesFromSeason,
    getTeamsBySeason,
    make_matplotlib_grid,
    saveFigure,
)
from utils.config import *
from utils.fullPitch import FullPitch

folder = os.path.join("imgs/", str(f"goalkeepers/zonalPassDistribution"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = FONT_FAMILY

COMPETITION_ID = 2
SEASON_ID = 27
ZONES_X = 6
ZONES_Y = 5
ZONE_WIDTH = PITCH_WIDTH / ZONES_X
ZONE_HEIGHT = PITCH_HEIGHT / ZONES_Y
VIZ_NAME = f"zonalPassDistribution_{COMPETITION_ID}_{SEASON_ID}"

# Data processing
teams = sorted(getTeamsBySeason(COMPETITION_ID, SEASON_ID))
passCountsMap = {}

for idx, team in enumerate(tqdm(teams, leave=False)):
    games = getTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)
    pass_counts = np.zeros((ZONES_Y, ZONES_X))

    for gameId in tqdm(games, leave=False):
        match = fetchMatch(gameId, load_360=True)
        df = match.events

        is_pass = df["type_name"] == "Pass"
        is_team = df["team_name"] == team
        is_gk = df["position_name"] == "Goalkeeper"
        gkPasses = df[is_team & is_gk & is_pass]
        # Considering Statsbomb data, a pass is successful if there is no "outcome" in the extra dict. Any outcome specification is negative (eg. Incomplete, Out, Unknown)
        gkPasses = gkPasses[
            gkPasses["extra"].apply(lambda x: "outcome" not in x["pass"])
        ]

        # Vectorized extraction of end locations and zone assignment
        end_locations = gkPasses["extra"].apply(lambda x: x["pass"]["end_location"])
        end_x = np.array([loc[0] for loc in end_locations])
        end_y = 80 - np.array([loc[1] for loc in end_locations])
        pass_counts += count_in_pitch_zones(
            end_x, end_y, ZONES_X, ZONES_Y, PITCH_WIDTH, PITCH_HEIGHT
        )

    passCountsMap[team] = pass_counts


# Drawing
fig, axes = make_matplotlib_grid(
    len(teams), max_cols=5, subplot_width=4, ratio=PITCH_RATIO
)
for idx, team in enumerate(teams):
    pitch = FullPitch()
    pitch.draw(ax=axes[idx])
    pass_counts = passCountsMap[team]
    team_max_pass_count = np.max(pass_counts)
    share_of_team_passes = pass_counts / pass_counts.sum()
    non_zero_shares = share_of_team_passes[share_of_team_passes > 0]
    label_threshold = np.percentile(non_zero_shares, 95)
    for i in range(ZONES_Y):
        for j in range(ZONES_X):
            count = pass_counts[i, j]
            alphaFactor = 1 * count / team_max_pass_count
            fill_rect = Rectangle(
                (j * ZONE_WIDTH, 80 - (i + 1) * ZONE_HEIGHT),
                ZONE_WIDTH,
                ZONE_HEIGHT,
                facecolor=PURPLE_HEX,
                edgecolor=GRAY_HEX,
                alpha=alphaFactor,
                linewidth=0.2,
                zorder=9,
            )
            axes[idx].add_patch(fill_rect)

            cur_zone_passes = share_of_team_passes[i, j]
            if cur_zone_passes >= label_threshold:
                axes[idx].text(
                    j * ZONE_WIDTH + ZONE_WIDTH / 2,
                    80 - (i + 1) * ZONE_HEIGHT + ZONE_HEIGHT / 2,
                    f"{cur_zone_passes*100:.1f}%",
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
    handleheight=1,
)

fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)

saveFigure(
    fig,
    f"{folder}/{VIZ_NAME}.png",
)
