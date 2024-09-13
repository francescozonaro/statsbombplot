import matplotlib.pyplot as plt
import os
import numpy as np

from utils import Pitch, change_range, adjust_color, derive_near_colors
from .matchBase import BaseMatchSBP


class ProgressiveSBP(BaseMatchSBP):

    def __init__(self):
        super().__init__()

    def _is_progressive(self, x, y, end_x, end_y):
        start_dist = np.sqrt((105 - x) ** 2 + (34 - y) ** 2)
        end_dist = np.sqrt((105 - end_x) ** 2 + (34 - end_y) ** 2)
        # passes to own half are always not progressive (Wyscout)
        thres = 100
        if x < 52.5 and end_x < 52.5:
            thres = 30
        elif x < 52.5 and end_x >= 52.5:
            thres = 15
        elif x >= 52.5 and end_x >= 52.5:
            thres = 10
        if thres > start_dist - end_dist:
            return False
        else:
            return True

    def _draw_player_progressive_events(
        self, events, player, colorMapping, drawAttempted, toggleTimestamp
    ):

        pitch = Pitch()
        f, ax = pitch.draw()

        events = events[events["player_name"] == player].reset_index(drop=True)

        events["end_location"] = events["extra"].apply(
            lambda x: (
                x["carry"]["end_location"]
                if "carry" in x
                else x["pass"]["end_location"]
            )
        )

        for i, event in events.iterrows():

            # Statsbomb pitch dimensions: 120 length, 80 width. My pitch dimensions: 105 length, 68 width.
            x = change_range(event.location[0], [0, 120], [0, 105])
            y = 68 - change_range(event.location[1], [0, 80], [0, 68])
            x_end = change_range(event.end_location[0], [0, 120], [0, 105])
            y_end = 68 - change_range(event.end_location[1], [0, 80], [0, 68])

            if event.type_name == "Carry":
                if self._is_progressive(x, y, x_end, y_end):
                    ax.scatter(
                        x,
                        y,
                        s=self.markerSize,
                        edgecolor="black",
                        linewidth=self.lineWidth,
                        facecolor=colorMapping[event["team_name"]][0],
                        zorder=7,
                        marker="o",
                    )
                    arrow_props = dict(
                        arrowstyle="->", color=colorMapping[event["team_name"]][0]
                    )
                    ax.annotate(
                        "",
                        xy=(x_end, y_end),
                        xytext=(x, y),
                        arrowprops=arrow_props,
                        zorder=6,
                    )
                    if toggleTimestamp:
                        ax.annotate(
                            f"{event.minute}:{str(event.second).zfill(2)}",
                            xy=(x, y),
                            xytext=(10, 10),
                            textcoords="offset points",
                            color="w",
                            ha="left",
                            fontsize=self.fontSize,
                            zorder=8,
                            bbox=dict(
                                boxstyle="round, pad=0.5",
                                fc=(0.1, 0.1, 0.1, 0.92),
                                ec=(1.0, 1.0, 1.0),
                                lw=1,
                            ),
                        )
            elif event.type_name == "Pass" and (
                drawAttempted or event.extra.get("pass", {}).get("outcome") is None
            ):
                if self._is_progressive(x, y, x_end, y_end):

                    ax.scatter(
                        x,
                        y,
                        s=self.markerSize,
                        edgecolor="black",
                        linewidth=self.lineWidth,
                        facecolor=colorMapping[event["team_name"]][1],
                        zorder=7,
                        marker="o",
                    )
                    arrow_props = dict(
                        arrowstyle="->", color=colorMapping[event["team_name"]][1]
                    )
                    ax.annotate(
                        "",
                        xy=(x_end, y_end),
                        xytext=(x, y),
                        arrowprops=arrow_props,
                        zorder=6,
                    )
                    if toggleTimestamp:
                        ax.annotate(
                            f"{event.minute}:{str(event.second).zfill(2)}",
                            xy=(x, y),
                            xytext=(10, 10),
                            textcoords="offset points",
                            color="w",
                            ha="left",
                            fontsize=self.fontSize,
                            zorder=8,
                            bbox=dict(
                                boxstyle="round, pad=0.5",
                                fc=(0.1, 0.1, 0.1, 0.92),
                                ec=(1.0, 1.0, 1.0),
                                lw=1,
                            ),
                        )

        legend_elements = [
            plt.scatter(
                [],
                [],
                s=self.markerSize,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=colorMapping[event["team_name"]][0],
                zorder=7,
                marker="o",
                label="Progressive Carry",
            ),
            plt.scatter(
                [],
                [],
                s=self.markerSize,
                edgecolor="black",
                linewidth=self.lineWidth,
                facecolor=colorMapping[event["team_name"]][1],
                zorder=7,
                marker="o",
                label="Progressive Pass",
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

        ax.text(1, 66, f"{player}", fontsize=self.fontSize, va="center", ha="left")
        ax.text(92.5, -2.1, "@francescozonaro", fontsize=self.fontSize, va="center")
        ax.text(
            0,
            -2.1,
            f"Wyscout definition of progressive pass/carry has been used.",
            fontsize=self.fontSize,
            va="center",
            ha="left",
        )

        if drawAttempted:
            ax.text(
                0,
                -4.1,
                f"The above plot is considering attempted passes, regardless of the outcome.",
                fontsize=self.fontSize,
                va="center",
                ha="left",
            )

        return f, ax

    def draw(self, g, data, teams, players):

        team_names = list(teams["team_name"])
        team_ids = list(teams["team_id"])

        colorMapping = {
            team_names[0]: derive_near_colors(self.homeColor),
            team_names[1]: derive_near_colors(self.awayColor),
        }

        print("Select a player or team by choosing the corresponding number:")
        for i, player in enumerate(players["player_name"], 1):
            print(f"{i}: {player}")
        print(f"{len(players) + 1}: {team_names[0]}")
        print(f"{len(players) + 2}: {team_names[1]}")
        print(f"{len(players) + 3}: All")

        choice = int(
            input("Enter the number of the player or team you want to select: ")
        )

        if choice <= len(players):
            pList = [players["player_name"].iloc[choice - 1]]
        elif choice == len(players) + 1:
            pList = players[players["team_id"] == team_ids[0]]["player_name"].tolist()
        elif choice == len(players) + 2:
            pList = players[players["team_id"] == team_ids[1]]["player_name"].tolist()
        elif choice == len(players) + 3:
            pList = players["player_name"].tolist()

        types = ["Pass", "Carry"]
        df = data[data["type_name"].isin(types)]

        for player in pList:
            f, _ = self._draw_player_progressive_events(
                df,
                player,
                colorMapping,
                drawAttempted=False,
                toggleTimestamp=True,
            )

            team = data[data["player_name"] == player]["team_name"].unique()[0]

            folder = f"imgs/{g}/{team}"
            filename = f"{folder}/ProgressiveSBP_{player}.png"
            os.makedirs(folder, exist_ok=True)
            f.savefig(filename, bbox_inches="tight", format="png", dpi=300)
            plt.close()
