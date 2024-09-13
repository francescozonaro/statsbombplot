import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

from utils import Pitch, changeRange


class ShotFreezed:

    def __init__(self):
        pass

    def draw(
        self,
        shot,
        playerNameToJerseyNumber,
    ):

        pitch = Pitch()
        f, ax = pitch.draw()

        x = changeRange(shot.location[0], [0, 120], [0, 105])
        y = 68 - changeRange(shot.location[1], [0, 80], [0, 68])
        end_x = changeRange(
            shot["extra"]["shot"]["end_location"][0], [0, 120], [0, 105]
        )
        end_y = 68 - changeRange(
            shot["extra"]["shot"]["end_location"][1], [0, 80], [0, 68]
        )
        shot_color = self.mainColor

        ax.scatter(
            x,
            y,
            s=self.markerSize * 2,
            edgecolor="black",
            linewidth=self.lineWidth,
            facecolor=shot_color,
            zorder=11,
            marker="*",
        )

        ax.plot(
            [x, end_x],
            [y, end_y],
            color=(0, 0, 0, 0.2),
            linewidth=self.lineWidth * 1.5,
            zorder=5,
            linestyle="--",
        )

        frame = shot["extra"]["shot"]["freeze_frame"]

        for player in frame:

            freezed_player_x = changeRange(player["location"][0], [0, 120], [0, 105])
            freezed_player_y = 68 - changeRange(player["location"][1], [0, 80], [0, 68])

            if player["teammate"]:
                freezed_player_color = self.mainColor
            else:
                freezed_player_color = self.altColor

            ax.scatter(
                freezed_player_x,
                freezed_player_y,
                s=self.markerSize * 2,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=freezed_player_color,
                zorder=9,
                marker="o",
            )

            ax.text(
                freezed_player_x + 0.025,
                freezed_player_y - 0.05,
                f"{playerNameToJerseyNumber[player['player']['name']]}",
                fontsize=self.fontSize - 2,
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
                s=self.markerSize * 1.5,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=shot_color,
                zorder=5,
                marker="*",
                label="Shot location",
            ),
            plt.scatter(
                [],
                [],
                s=self.markerSize,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=self.mainColor,
                zorder=5,
                marker="o",
                label="Teammate",
            ),
            plt.scatter(
                [],
                [],
                s=self.markerSize,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=self.altColor,
                zorder=5,
                marker="o",
                label="Opponent",
            ),
        ]

        return f, ax, legendElements
