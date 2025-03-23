import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import os
import matplotlib.colors as mcolors

from utils import (
    Pitch,
    addLegend,
    addNotes,
    saveFigure,
    fetchMatch,
    fetchRandomMatch,
)


class Shotmap:

    def __init__(self, homeColor, awayColor):
        self.homeColor = homeColor
        self.awayColor = awayColor
        self.markerSize = 120
        self.lineWidth = 0.7

    def draw(self, shots, homeTeamId):

        pitch = Pitch()
        f, ax = pitch.draw()

        for _, shot in shots.iterrows():
            shotxG = round(shot.extra["shot"]["statsbomb_xg"], 3)
            scaledxG = 0.1 + (1 - 0.1) * (shotxG / 0.25)
            scaledxG = min(scaledxG, 1)

            shotTechnique = shot.extra["shot"]["technique"]["name"]
            if shotTechnique == "Normal":
                shotTechnique = shot.extra["shot"]["body_part"]["name"]

            if shot.team_id != homeTeamId:
                x = shot.location[0]
                y = 80 - shot.location[1]
                shotColor = mcolors.to_rgba(self.homeColor, scaledxG)
            else:
                x = 120 - shot.location[0]
                y = shot.location[1]
                shotColor = mcolors.to_rgba(self.awayColor, scaledxG)

            if shot.extra["shot"]["outcome"]["name"] == "Goal":
                ax.scatter(
                    x,
                    y,
                    s=self.markerSize * 1.5,
                    edgecolor="black",
                    linewidth=self.lineWidth,
                    facecolor=shotColor,
                    zorder=7,
                    marker="*",
                )
            elif shot.extra["shot"]["outcome"]["name"] == "Saved":
                ax.scatter(
                    x,
                    y,
                    s=self.markerSize,
                    edgecolor="black",
                    linewidth=self.lineWidth,
                    facecolor=shotColor,
                    zorder=6,
                    marker="o",
                )
            else:
                ax.scatter(
                    x,
                    y,
                    s=self.markerSize,
                    edgecolor="black",
                    linewidth=self.lineWidth,
                    facecolor=shotColor,
                    zorder=5,
                    marker="X",
                )

        legend_elements = [
            plt.scatter(
                [],
                [],
                s=90,
                edgecolor="black",
                linewidth=0.6,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="*",
                label="Goal",
            ),
            plt.scatter(
                [],
                [],
                s=90,
                edgecolor="black",
                linewidth=0.6,
                facecolor=(1, 1, 1, 0.8),
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
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="X",
                label="Off Target",
            ),
            plt.scatter(
                [],
                [],
                s=30,
                edgecolor="black",
                linewidth=0.6,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="o",
                label="Low xG",
            ),
            plt.scatter(
                [],
                [],
                s=90,
                edgecolor="black",
                linewidth=0.6,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="o",
                label="High xG",
            ),
        ]

        return f, ax, legend_elements


match = fetchRandomMatch(seed=602210)
folder = os.path.join("imgs/", str(match.gameId))
os.makedirs(folder, exist_ok=True)

homeTeamColor = match.homeTeamColor
awayTeamColor = match.awayTeamColor

shotMap = Shotmap(homeTeamColor, awayTeamColor)
shots = match.events[match.events["type_name"] == "Shot"].reset_index(drop=True)
validShots = shots[(shots["period_id"] < 5)]

fig, ax, legendElements = shotMap.draw(validShots, match.homeTeamId)
extra = [f"{match.homeTeamName} vs {match.awayTeamName}"]
addLegend(ax, legendElements)
addNotes(ax, author="@francescozonaro", extra_text=extra)
saveFigure(fig, f"{folder}/shotmap_{match.gameId}.png")
