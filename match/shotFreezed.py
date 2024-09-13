import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import os

from utils import Pitch, change_range
from .matchBase import BaseMatchSBP


class ShotfreezedSBP(BaseMatchSBP):

    def __init__(self):
        super().__init__()

    def _draw_shot_freezed(
        self,
        event,
        playerNameToJerseyNumber,
    ):

        pitch = Pitch()
        f, ax = pitch.draw()

        shot_xG = round(event.extra["shot"]["statsbomb_xg"], 3)
        shot_technique = event.extra["shot"]["technique"]["name"]

        if shot_technique == "Normal":
            shot_technique = event.extra["shot"]["body_part"]["name"]

        x = change_range(event.location[0], [0, 120], [0, 105])
        y = 68 - change_range(event.location[1], [0, 80], [0, 68])
        end_x = change_range(
            event["extra"]["shot"]["end_location"][0], [0, 120], [0, 105]
        )
        end_y = 68 - change_range(
            event["extra"]["shot"]["end_location"][1], [0, 80], [0, 68]
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

        frame = event["extra"]["shot"]["freeze_frame"]

        for player in frame:

            freezed_player_x = change_range(player["location"][0], [0, 120], [0, 105])
            freezed_player_y = 68 - change_range(
                player["location"][1], [0, 80], [0, 68]
            )

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
                f"{playerNameToJerseyNumber[player['player']['name']]}",  # text to display (customize as needed)
                fontsize=self.fontSize - 2,
                zorder=9,
                ha="center",
                va="center",
                color="white",
                path_effects=[
                    path_effects.withStroke(linewidth=1.5, foreground="black")
                ],
            )

        legend_elements = [
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

        ax.legend(
            handles=legend_elements,
            loc="upper center",
            ncol=len(legend_elements),
            bbox_to_anchor=(0.5, 0.99),
            fontsize=self.fontSize,
            fancybox=True,
            frameon=True,
            handletextpad=0.5,
        )

        ax.text(92.5, -2.1, "@francescozonaro", fontsize=self.fontSize, va="center")
        ax.text(
            1,
            66,
            f"{event['player_name']} | {event['extra']['shot']['outcome']['name']} | {shot_xG} xG",
            fontsize=self.fontSize,
            va="center",
            ha="left",
        )
        ax.text(
            1,
            64,
            f"{event['minute']}:{event['second']}",
            fontsize=self.fontSize,
            va="center",
            ha="left",
        )

        return f, ax

    def draw(self, g, data, teams, players):

        playerNameToJerseyNumber = players.set_index("player_name")[
            "jersey_number"
        ].to_dict()

        df = data[data["type_name"] == "Shot"].reset_index(drop=True)

        for i, row in df.iterrows():
            try:
                f, ax = self._draw_shot_freezed(
                    row,
                    playerNameToJerseyNumber,
                )

                folder = f"imgs/{g}/{row['team_name']}"
                filename = f"{folder}/ShotfreezeSBP_{i}_{row['player_name']}.png"
                os.makedirs(folder, exist_ok=True)
                f.savefig(filename, bbox_inches="tight", format="png", dpi=300)
                plt.close()
            except Exception as e:
                plt.close()
