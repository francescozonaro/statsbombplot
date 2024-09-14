import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

from utils import Pitch


class ShotFrame:

    def __init__(self, mainColor, altColor):
        self.mainColor = mainColor
        self.altColor = altColor

    def draw(
        self,
        x,
        y,
        end_x,
        end_y,
        frame,
        playerNameToJerseyNumber,
    ):

        pitch = Pitch()
        f, ax = pitch.draw()

        ax.scatter(
            x,
            y,
            s=120,
            edgecolor="black",
            linewidth=0.6,
            facecolor=self.mainColor,
            zorder=11,
            marker="*",
        )

        ax.plot(
            [x, end_x],
            [y, end_y],
            color=(0, 0, 0, 0.2),
            linewidth=0.9,
            zorder=5,
            linestyle="--",
        )

        for player in frame:

            freezed_player_x = player["location"][0]
            freezed_player_y = 80 - player["location"][1]

            if player["teammate"]:
                freezed_player_color = self.mainColor
            else:
                freezed_player_color = self.altColor

            ax.scatter(
                freezed_player_x,
                freezed_player_y,
                s=120,
                edgecolor="black",
                linewidth=0.6,
                facecolor=freezed_player_color,
                zorder=9,
                marker="o",
            )

            ax.text(
                freezed_player_x + 0.025,
                freezed_player_y - 0.05,
                f"{playerNameToJerseyNumber[player['player']['name']]}",
                fontsize=6,
                zorder=9,
                ha="center",
                va="center",
                color="white",
                path_effects=[
                    path_effects.withStroke(linewidth=1.5, foreground="black")
                ],
            )

        legendElements = [
            plt.scatter(
                [],
                [],
                s=90,
                edgecolor="black",
                linewidth=0.6,
                facecolor=self.mainColor,
                zorder=5,
                marker="*",
                label="Shot location",
            ),
            plt.scatter(
                [],
                [],
                s=60,
                edgecolor="black",
                linewidth=0.6,
                facecolor=self.mainColor,
                zorder=5,
                marker="o",
                label="Teammate",
            ),
            plt.scatter(
                [],
                [],
                s=60,
                edgecolor="black",
                linewidth=0.6,
                facecolor=self.altColor,
                zorder=5,
                marker="o",
                label="Opponent",
            ),
        ]

        plt.close()
        return f, ax, legendElements
