import os

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

from utils.commons import fetchMatch, saveFigure
from utils.config import FIG_BACKGROUND_COLOR
from utils.fullPitch import FullPitch

GAME_ID = 3795506  # EURO 2020 Final
HOME_TEAM_COLOR = "#3f8ae6"
AWAY_TEAM_COLOR = "#f04a5f"
MARKER_SIZE = 120
LINE_WIDTH = 0.7
OUTCOME_STYLE = {
    "Goal": ("*", MARKER_SIZE * 1.5, 7),
    "Saved": ("o", MARKER_SIZE, 6),
}

folder = os.path.join("imgs/", str(GAME_ID))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

### Data ###
match = fetchMatch(gameId=GAME_ID)
df = match.events
isShot = df["type_name"] == "Shot"
isValidPeriod = df["period_id"] < 5
sdf = df[isShot & isValidPeriod].copy()
isHome = sdf["team_id"] == match.homeTeamId
sdf.loc[~isHome, "plot_x"] = sdf.loc[~isHome, "location"].map(lambda loc: loc[0])
sdf.loc[~isHome, "plot_y"] = sdf.loc[~isHome, "location"].map(lambda loc: 80 - loc[1])
sdf.loc[isHome, "plot_x"] = sdf.loc[isHome, "location"].map(lambda loc: 120 - loc[0])
sdf.loc[isHome, "plot_y"] = sdf.loc[isHome, "location"].map(lambda loc: loc[1])
sdf["team_color"] = np.where(isHome, HOME_TEAM_COLOR, AWAY_TEAM_COLOR)

### Figure ###
pitch = FullPitch()
fig, ax = plt.subplots(1, 1, figsize=(15, 15 * (80 / 120)), dpi=300)
fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)
ax.set_facecolor(FIG_BACKGROUND_COLOR)
pitch.draw(ax)

for _, shot in sdf.iterrows():
    shot_extra = shot.extra["shot"]
    shot_xg = round(shot_extra["statsbomb_xg"], 3)
    scaled_xg = np.clip(shot_xg / 0.25, 0.1, 1.0)
    outcome = shot_extra["outcome"]["name"]
    shotTechnique = shot_extra["technique"]["name"]
    body_part = shot_extra["body_part"]["name"]
    shotColor = mcolors.to_rgba(shot.team_color, scaled_xg)

    marker, size, zorder = OUTCOME_STYLE.get(outcome, ("X", MARKER_SIZE, 5))
    ax.scatter(
        shot.plot_x,
        shot.plot_y,
        s=size,
        edgecolor="black",
        linewidth=LINE_WIDTH,
        facecolor=shotColor,
        zorder=zorder,
        marker=marker,
    )


legend_markers = [
    ("X", "Off Target"),
    ("o", "On Target"),
    ("*", "Goal"),
]
legendElements = [
    plt.scatter(
        [],
        [],
        s=90,
        marker=marker,
        label=label,
        edgecolor="black",
        linewidth=0.6,
        facecolor=HOME_TEAM_COLOR,
        zorder=5,
    )
    for marker, label in legend_markers
]

extra = [f"{match.homeTeamName} vs {match.awayTeamName}"]
pitch.addPitchLegend(ax, legendElements)
pitch.addPitchNotes(ax, extra_text=extra)
saveFigure(fig, f"{folder}/shotmap_{match.gameId}.png")
