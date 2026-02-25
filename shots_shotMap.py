import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import os
import matplotlib.colors as mcolors

from utils.fullPitch import FullPitch
from utils.commons import saveFigure, getRandomMatchId, fetchMatch
from utils.config import *

GAME_ID = 3795506  # EURO 2020 Final

folder = os.path.join("imgs/", str(GAME_ID))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

awayTeamColor = "#3f8ae6"
homeTeamColor = "#f04a5f"
markerSize = 120
lineWidth = 0.7

# match = fetchMatch(gameId=getRandomMatchId(seed=602210))
match = fetchMatch(gameId=GAME_ID)
df = match.events
isShot = df["type_name"] == "Shot"
isValidPeriod = df["period_id"] < 5
shots = df[isShot & isValidPeriod]

pitch = FullPitch()
fig, ax = plt.subplots(1, 1, figsize=(15, 15 * (80 / 120)), dpi=300)
fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)
ax.set_facecolor(FIG_BACKGROUND_COLOR)
pitch.draw(ax)

for _, shot in shots.iterrows():
    shotxG = round(shot.extra["shot"]["statsbomb_xg"], 3)
    scaledxG = 0.1 + (1 - 0.1) * (shotxG / 0.25)
    scaledxG = min(scaledxG, 1)

    shotTechnique = shot.extra["shot"]["technique"]["name"]
    if shotTechnique == "Normal":
        shotTechnique = shot.extra["shot"]["body_part"]["name"]

    if shot.team_id != match.homeTeamId:
        x = shot.location[0]
        y = 80 - shot.location[1]
        shotColor = mcolors.to_rgba(homeTeamColor, scaledxG)
    else:
        x = 120 - shot.location[0]
        y = shot.location[1]
        shotColor = mcolors.to_rgba(awayTeamColor, scaledxG)

    if shot.extra["shot"]["outcome"]["name"] == "Goal":
        ax.scatter(
            x,
            y,
            s=markerSize * 1.5,
            edgecolor="black",
            linewidth=lineWidth,
            facecolor=shotColor,
            zorder=7,
            marker="*",
        )
    elif shot.extra["shot"]["outcome"]["name"] == "Saved":
        ax.scatter(
            x,
            y,
            s=markerSize,
            edgecolor="black",
            linewidth=lineWidth,
            facecolor=shotColor,
            zorder=6,
            marker="o",
        )
    else:
        ax.scatter(
            x,
            y,
            s=markerSize,
            edgecolor="black",
            linewidth=lineWidth,
            facecolor=shotColor,
            zorder=5,
            marker="X",
        )

legendElements = [
    plt.scatter(
        [],
        [],
        s=90,
        edgecolor="black",
        linewidth=0.6,
        facecolor=awayTeamColor,
        zorder=5,
        marker="X",
        label="Off Target",
    ),
    plt.scatter(
        [],
        [],
        s=90,
        edgecolor="black",
        linewidth=0.6,
        facecolor=awayTeamColor,
        zorder=5,
        marker="o",
        label="On Target",
    ),
    plt.scatter(
        [],
        [],
        s=90,
        edgecolor="black",
        linewidth=0.6,
        facecolor=awayTeamColor,
        zorder=5,
        marker="*",
        label="Goal",
    ),
]

extra = [f"{match.homeTeamName} vs {match.awayTeamName}"]
pitch.addPitchLegend(ax, legendElements)
pitch.addPitchNotes(ax, extra_text=extra)
saveFigure(fig, f"{folder}/shotmap_{match.gameId}.png")
