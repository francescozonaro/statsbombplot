"""

Based on Sergio Llana (@SergioMinuto90) passing network created on Sun Apr 19 2020

Modified Jun 24 2023

@author: Francesco Zonaro

"""

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from utils import Pitch


class PassingNetwork:

    def __init__(self, markerColor):
        self.markerColor = markerColor

    def draw(self, playerPassCount, pairPassCount, playerPosition):

        pitch = Pitch()
        f, ax = pitch.draw()

        maxPlayerPassCount = playerPassCount.num_passes.max()
        maxPairPassCount = pairPassCount.num_passes.max()

        for pair_key, row in pairPassCount.iterrows():
            player1, player2 = pair_key.split("_")
            player1_x = playerPosition.loc[player1]["x"]
            player1_y = playerPosition.loc[player1]["y"]
            player2_x = playerPosition.loc[player2]["x"]
            player2_y = playerPosition.loc[player2]["y"]

            numPasses = row["num_passes"]
            lineWidth = 3.5 * numPasses / maxPairPassCount

            ax.plot(
                [player1_x, player2_x],
                [player1_y, player2_y],
                linestyle="-",
                alpha=0.4,
                lw=lineWidth,
                zorder=3,
                color=self.markerColor,
            )

        for playerName, row in playerPassCount.iterrows():
            playerX = playerPosition.loc[playerName]["x"]
            playerY = playerPosition.loc[playerName]["y"]
            numPasses = row["num_passes"]
            markerSize = 100 * numPasses / maxPlayerPassCount

            ax.plot(
                playerX,
                playerY,
                ".",
                markersize=markerSize,
                color=self.markerColor,
                zorder=5,
            )
            ax.plot(
                playerX,
                playerY,
                ".",
                markersize=markerSize - 15,
                color="white",
                zorder=6,
            )
            ax.annotate(
                playerName.split()[-1],
                xy=(playerX, playerY),
                ha="center",
                va="center",
                zorder=7,
                weight="bold",
                size=8,
                path_effects=[pe.withStroke(linewidth=2, foreground="white")],
            )

        legendElements = [
            plt.scatter(
                [],
                [],
                s=15,
                edgecolor=self.markerColor,
                linewidth=1,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="o",
                label="Few passes made",
            ),
            plt.scatter(
                [],
                [],
                s=150,
                edgecolor=self.markerColor,
                linewidth=2,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="o",
                label="Many passes made",
            ),
            mlines.Line2D(
                [],
                [],
                color=self.markerColor,
                linewidth=1,
                linestyle="solid",
                label=f"Pair combines rarely",
            ),
            mlines.Line2D(
                [],
                [],
                color=self.markerColor,
                linewidth=4,
                linestyle="solid",
                label=f"Pair combines frequently",
            ),
        ]
        return f, ax, legendElements
