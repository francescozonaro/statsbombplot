import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from common import config, change_range, get_statsbomb_api, Pitch


class ShotframeSB:

    def __init__(self):
        self.api = get_statsbomb_api()
        self.markersize = 100 * (config["fig_size"] / 12)
        self.linewidth = 0.5 * (config["fig_size"] / 12)

    def _draw_shotFreezed(
        self,
        event,
        filename,
        playerNameToJerseyNumber,
        color=(0.5, 0.78, 0.97, 1),
        opp_color=(1, 0.376, 0.137, 0.8),
    ):

        pitch = Pitch(config)
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
        shot_color = color

        ax.scatter(
            x,
            y,
            s=self.markersize * 1.5,
            edgecolor="black",
            linewidth=linewidth,
            facecolor=shot_color,
            zorder=6,
            marker="*",
        )

        ax.plot(
            [x, end_x],
            [y, end_y],
            color=(0, 0, 0, 0.2),
            linewidth=self.linewidth * 1.5,
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
                freezed_player_color = color
            else:
                freezed_player_color = opp_color

            ax.scatter(
                freezed_player_x,
                freezed_player_y,
                s=self.markersize,
                edgecolor="black",
                linewidth=self.linewidth,
                facecolor=freezed_player_color,
                zorder=8,
                marker="o",
            )

            ax.text(
                freezed_player_x + 0.025,
                freezed_player_y - 0.05,
                f"{playerNameToJerseyNumber[player['player']['name']]}",  # text to display (customize as needed)
                fontsize=5,
                zorder=10,
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
                s=self.markersize * 1.5,
                edgecolor="black",
                linewidth=self.linewidth,
                facecolor=shot_color,
                zorder=5,
                marker="*",
                label="Shot location",
            ),
            plt.scatter(
                [],
                [],
                s=self.markersize,
                edgecolor="black",
                linewidth=linewidth,
                facecolor=color,
                zorder=5,
                marker="o",
                label="Teammate",
            ),
            plt.scatter(
                [],
                [],
                s=self.markersize,
                edgecolor="black",
                linewidth=self.linewidth,
                facecolor=opp_color,
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
            fontsize=10,
            fancybox=True,
            frameon=True,
            handletextpad=0.5,
        )

        ax.text(92.5, -2.1, "@francescozonaro", fontsize=10, va="center")
        ax.text(
            1,
            66,
            f"{event['player_name']} | {event['extra']['shot']['outcome']['name']} | {shot_xG} xG",
            fontsize=10,
            va="center",
            ha="left",
        )
        ax.text(
            1,
            64,
            f"{event['minute']}:{event['second']}",
            fontsize=10,
            va="center",
            ha="left",
        )
        plt.savefig(f"imgs/{filename}.png", bbox_inches="tight", format="png", dpi=300)
        plt.close()

    def draw(self, g):
        api = get_statsbomb_api()
        events = api.events(game_id=g)
        players = api.players(game_id=g)
        playerNameToJerseyNumber = players.set_index("player_name")[
            "jersey_number"
        ].to_dict()

        events = events[
            ["player_name", "type_name", "extra", "location", "minute", "second"]
        ].reset_index(drop=True)
        events = events[events["type_name"] == "Shot"].reset_index(drop=True)

        for i, row in events.iterrows():
            try:
                self._draw_shotFreezed(
                    row,
                    f"freezing_{g}_shot_{i}_{row['player_name']}",
                    playerNameToJerseyNumber,
                    color=(1, 0.376, 0.137, 0.8),
                    opp_color=(0.5, 0.78, 0.97, 1),
                )
            except Exception as e:
                pass
