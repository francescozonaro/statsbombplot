import matplotlib.pyplot as plt
from common import config, change_range, get_statsbomb_api, Pitch
import numpy as np


class ProgressiveSB:

    def __init__(self):
        self.api = get_statsbomb_api()
        self.markersize = 50 * (config["fig_size"] / 12)
        self.linewidth = 0.5 * (config["fig_size"] / 12)
        self.fontsize = 6 * (config["fig_size"] / 12)

    def _is_progressive(self, x, y, end_x, end_y):
        start_dist = np.sqrt((105 - x) ** 2 + (34 - y) ** 2)
        end_dist = np.sqrt((105 - end_x) ** 2 + (34 - end_y) ** 2)
        # passes to own half are always not progressive
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
        self, events, player, filename, drawAttempted, toggleTimestamp
    ):

        pitch = Pitch(config)
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
                        s=self.markersize,
                        edgecolor="black",
                        linewidth=self.linewidth,
                        facecolor="#f4a261",
                        zorder=7,
                        marker="o",
                    )
                    arrow_props = dict(arrowstyle="->", color="#f4a261")
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
                            fontsize=self.fontsize,
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
                        s=self.markersize,
                        edgecolor="black",
                        linewidth=self.linewidth,
                        facecolor="#2a9d8f",
                        zorder=7,
                        marker="o",
                    )
                    arrow_props = dict(arrowstyle="->", color="#2a9d8f")
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
                            fontsize=self.fontsize,
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
                s=self.markersize,
                edgecolor="black",
                linewidth=self.linewidth,
                facecolor="#f4a261",
                zorder=7,
                marker="o",
                label="Progressive Carry",
            ),
            plt.scatter(
                [],
                [],
                s=self.markersize,
                edgecolor="black",
                linewidth=self.linewidth,
                facecolor="#2a9d8f",
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
            fontsize=10,
            fancybox=True,
            frameon=True,
            handletextpad=0.5,
        )

        ax.text(1, 66, f"{player}", fontsize=10, va="center", ha="left")
        ax.text(92.5, -2.1, "@francescozonaro", fontsize=10, va="center")
        ax.text(
            0,
            -2.1,
            f"Wyscout definition of progressive pass/carry has been used.",
            fontsize=7,
            va="center",
            ha="left",
        )

        if drawAttempted:
            ax.text(
                0,
                -4.1,
                f"The above plot is considering attempted passes, regardless of the outcome.",
                fontsize=7,
                va="center",
                ha="left",
            )

        plt.savefig(f"imgs/{filename}.png", bbox_inches="tight", format="png", dpi=300)

    def draw(self, g):
        api = get_statsbomb_api()

        try:
            df_events = api.events(game_id=g, load_360=True)
        except:
            df_events = api.events(game_id=g, load_360=False)

        teams = list(df_events["team_name"].unique())
        team_ids = list(df_events["team_id"].unique())
        df_players = api.players(game_id=g)

        print("Select a player or team by choosing the corresponding number:")
        for i, player in enumerate(df_players["player_name"], 1):
            print(f"{i}: {player}")
        print(f"{len(df_players) + 1}: {teams[0]}")
        print(f"{len(df_players) + 2}: {teams[1]}")
        print(f"{len(df_players) + 3}: All")

        choice = int(
            input("Enter the number of the player or team you want to select: ")
        )

        if choice <= len(df_players):
            fdp = [df_players["player_name"].iloc[choice - 1]]
        elif choice == len(df_players) + 1:
            fdp = df_players[df_players["team_id"] == team_ids[0]][
                "player_name"
            ].tolist()
        elif choice == len(df_players) + 2:
            fdp = df_players[df_players["team_id"] == team_ids[1]][
                "player_name"
            ].tolist()
        elif choice == len(df_players) + 3:
            fdp = df_players["player_name"].tolist()

        types = ["Pass", "Carry"]
        df = df_events[df_events["type_name"].isin(types)]

        for player in fdp:
            self._draw_player_progressive_events(
                df,
                player,
                f"{g}_progressive_{player}",
                drawAttempted=False,
                toggleTimestamp=True,
            )
