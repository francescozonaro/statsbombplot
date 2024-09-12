import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import os

from common import Pitch, change_range
from .base import BaseSBP


class ScatterplotSBP(BaseSBP):

    def __init__(self):
        super().__init__()
        self.mainColor = self.homeColor

    def _draw_event_type_scatter(
        self,
        events,
        label,
        draw_mean_height=True,
    ):

        pitch = Pitch()
        f, ax = pitch.draw()

        count_opponent_half = 0

        for i, event in events.iterrows():

            # Statsbomb pitch dimensions: 120 length, 80 width
            x = change_range(event.location[0], [0, 120], [0, 105])
            y = change_range(event.location[1], [0, 80], [0, 68])

            if x > 52.5:
                count_opponent_half += 1

            ax.scatter(
                x,
                y,
                s=self.markerSize,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=self.mainColor,
                zorder=7,
                marker="o",
            )

        legend_elements = [
            plt.scatter(
                [],
                [],
                s=self.markerSize,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=self.mainColor,
                zorder=7,
                marker="o",
                label=label,
            )
        ]

        if draw_mean_height:
            events["X"] = events["location"].apply(lambda loc: loc[0])
            events["Y"] = events["location"].apply(lambda loc: loc[1])

            # Group by the 'event_id' and calculate the mean X and Y for each ball recovery
            mean_coordinates = events[["X", "Y"]].mean()
            avg_ball_recovery_x = change_range(mean_coordinates.X, [0, 120], [0, 105])

            ax.axvline(
                x=avg_ball_recovery_x,
                ymin=0.0625,
                ymax=0.9375,
                color=(0.88, 0.48, 0.37, 0.8),
                linewidth=2,
                zorder=4,
                linestyle="dashed",
            )

            legend_elements.extend(
                [
                    mlines.Line2D(
                        [],
                        [],
                        color=(0.88, 0.48, 0.37, 0.8),
                        linewidth=2,
                        linestyle="dashed",
                        label=f"Mean Height of {label}",
                    )
                ]
            )

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

        ax.text(92.5, -2.1, "@francescozonaro", fontsize=10, va="center")
        ax.text(
            0,
            -2.1,
            f"Number of events: {len(events)}",
            fontsize=7,
            va="center",
            ha="left",
        )

        percentage_opponent_half = round(100 * count_opponent_half / len(events), 2)
        ax.text(
            0,
            -4.1,
            f"Percentage in opponent half: {percentage_opponent_half}%",
            fontsize=7,
            va="center",
            ha="left",
        )

        return f, ax

    def draw(
        self,
        g,
        data,
        teams,
        mode,
    ):

        team_names = list(teams["team_name"])
        team_ids = list(teams["team_id"])
        is_home = list(teams["isHome"])

        for team_id, team_name, home in zip(team_ids, team_names, is_home):

            opposing_team_id = next(t for t in team_ids if t != team_id)
            self.mainColor = self.homeColor if home else self.awayColor

            if mode == "defensive":
                event_type_name = "Def Action"
                types = [
                    "Block",
                    "Interception",
                    "Clearance",
                    "Ball Recovery",
                ]
                df = data[data["type_name"].isin(types)]
                df = df[df["team_id"] == team_id].reset_index(drop=True)
                # For this plot we consider only situations where an opponent has the ball
                df = df[df["possession_team_id"] == opposing_team_id]
                # Ignoring the keeper
                df = df[df["position_name"] != "Goalkeeper"]
            elif mode == "passing":
                event_type_name = "Passing"
                types = ["Pass"]
                df = data[data["type_name"].isin(types)]
                df = df[df["team_id"] == team_id].reset_index(drop=True)
            else:
                raise ValueError(f"{mode} isn't supported")

            event_type = f"{team_name} {event_type_name}"

            f, _ = self._draw_event_type_scatter(
                df,
                label=event_type,
                draw_mean_height=True,
            )

            folder = f"imgs/{g}/{team_name}"
            filename = f"{folder}/ScatterplotSBP_{event_type_name.lower().replace(' ', '')}.png"
            os.makedirs(folder, exist_ok=True)
            f.savefig(filename, bbox_inches="tight", format="png", dpi=300)
            plt.close()
