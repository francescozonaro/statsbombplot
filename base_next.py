import os
import urllib.request

import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

from utils.commons import (
    fetchMatch,
    getTeamMatchesFromSeason,
    getTeamsBySeason,
    saveFigure,
)
from utils.config import *
from utils.fullPitch import FullPitch

COMPETITION_ID = 2
SEASON_ID = 27
VIZ_COLOR = "#a41212"
N_COLS = 5
N_ROWS = 4
SUBPLOT_WIDTH = 4
NUM_ZONES_X = 5
NUM_ZONES_Y = 1
RECT_X = PITCH_WIDTH / NUM_ZONES_X
RECT_Y = PITCH_HEIGHT / NUM_ZONES_Y

folder = os.path.join("imgs/", "test")
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

fig_width = SUBPLOT_WIDTH * N_COLS
fig_height = SUBPLOT_WIDTH * PITCH_RATIO * N_ROWS
fig, axes = plt.subplots(N_ROWS, N_COLS, figsize=(fig_width, fig_height))
axes = axes.flatten()
fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)

teams = sorted(getTeamsBySeason(competitionId=COMPETITION_ID, seasonId=SEASON_ID))
for idx, team in enumerate(tqdm(teams, leave=False)):
    games = getTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)
    for gameId in tqdm(games, leave=False):
        match = fetchMatch(gameId, load_360=True)
        df = match.events


for idx, team in enumerate(teams):
    pitch = FullPitch()
    pitch.draw(ax=axes[idx])
    axes[idx].set_facecolor(FIG_BACKGROUND_COLOR)
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
        edgecolor="black",
        linewidth=0.6,
        facecolor="#ffffff",
        zorder=5,
        marker="s",
        label="Few",
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
        label="Many",
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
    f"{folder}/test.png",
)
