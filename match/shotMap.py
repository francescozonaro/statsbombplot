import matplotlib.pyplot as plt
import os

from common import Pitch, change_range
from .base import BaseSBP


class ShotmapSBP(BaseSBP):

    def __init__(self):
        super().__init__()

    def _draw_shotmap(self, events, teams):

        pitch = Pitch()
        f, ax = pitch.draw()

        team_names = list(teams["team_name"])
        team_ids = list(teams["team_id"])

        for i, event in events.iterrows():
            shot_xG = round(event.extra["shot"]["statsbomb_xg"], 3)
            multiplier_xG = round(change_range(shot_xG, [0, 1], [1, 5]), 3)
            markersize = self.markerSize * multiplier_xG

            shot_technique = event.extra["shot"]["technique"]["name"]

            if shot_technique == "Normal":
                shot_technique = event.extra["shot"]["body_part"]["name"]

            # Statsbomb pitch dimensions: 120 length, 80 width
            if event.team_id != team_ids[0]:
                x = change_range(event.location[0], [0, 120], [0, 105])
                y = 68 - change_range(event.location[1], [0, 80], [0, 68])
                shot_color = self.awayColor
            else:
                x = 105 - change_range(event.location[0], [0, 120], [0, 105])
                y = change_range(event.location[1], [0, 80], [0, 68])
                shot_color = self.homeColor

            if event.extra["shot"]["outcome"]["name"] == "Goal":
                ax.scatter(
                    x,
                    y,
                    s=markersize * 1.5,
                    edgecolor="black",
                    linewidth=self.lineWidth,
                    facecolor=shot_color,
                    zorder=7,
                    marker="*",
                )
            elif event.extra["shot"]["outcome"]["name"] == "Saved":
                ax.scatter(
                    x,
                    y,
                    s=markersize,
                    edgecolor="black",
                    linewidth=self.lineWidth,
                    facecolor=shot_color,
                    zorder=6,
                    marker="o",
                )
            else:
                ax.scatter(
                    x,
                    y,
                    s=markersize,
                    edgecolor="black",
                    linewidth=self.lineWidth,
                    facecolor=shot_color,
                    zorder=5,
                    marker="X",
                )

        legend_elements = [
            plt.scatter(
                [],
                [],
                s=self.markerSize * 1.2,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="*",
                label="Goal",
            ),
            plt.scatter(
                [],
                [],
                s=self.markerSize,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="o",
                label="On Target",
            ),
            plt.scatter(
                [],
                [],
                s=self.markerSize,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="X",
                label="Off Target",
            ),
            plt.scatter(
                [],
                [],
                s=self.markerSize / 3,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="o",
                label="Low xG",
            ),
            plt.scatter(
                [],
                [],
                s=self.markerSize,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="o",
                label="High xG",
            ),
        ]

        legend = ax.legend(
            handles=legend_elements,
            loc="upper center",
            ncol=len(legend_elements),
            bbox_to_anchor=(0.5, 0.99),
            fontsize=self.fontSize,
            fancybox=True,
            frameon=True,
            handletextpad=0.5,
        )

        ax.text(94.5, -2.1, "@francescozonaro", fontsize=self.fontSize, va="center")

        ax.text(
            1, 66, f"{team_names[0]}", fontsize=self.fontSize, va="center", ha="left"
        )

        ax.text(
            104, 66, f"{team_names[1]}", fontsize=self.fontSize, va="center", ha="right"
        )

        return f, ax

    def draw(self, g, data, teams):

        df = data[
            (data["type_name"] == "Shot") & (data["period_id"] < 5)  # No penalties
        ].reset_index(drop=True)

        f, _ = self._draw_shotmap(df, teams)

        folder = f"imgs/{g}"
        filename = f"{folder}/shotmap.png"
        os.makedirs(folder, exist_ok=True)
        f.savefig(filename, bbox_inches="tight", format="png", dpi=300)
        plt.close()
