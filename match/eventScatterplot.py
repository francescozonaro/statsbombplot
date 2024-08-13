import matplotlib.pyplot as plt
from common import config, change_range, get_statsbomb_api
from common import Pitch
import matplotlib.lines as mlines


class ScatterplotSB:

    def __init__(self):
        self.api = get_statsbomb_api()
        self.markersize = 50 * (config["fig_size"] / 12)
        self.linewidth = 0.5 * (config["fig_size"] / 12)

    def _draw_event_type_scatter(
        self,
        events,
        filename,
        event_type,
        draw_mean_height=True,
        marker_shape="o",
        marker_color=(0.765, 0.388, 0.961, 0.8),
    ):

        pitch = Pitch(config)
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
                s=self.markersize,
                edgecolor="black",
                linewidth=self.linewidth,
                facecolor=marker_color,
                zorder=7,
                marker=marker_shape,
            )

        legend_elements = [
            plt.scatter(
                [],
                [],
                s=self.markersize,
                edgecolor="black",
                linewidth=self.linewidth,
                facecolor=marker_color,
                zorder=7,
                marker=marker_shape,
                label=event_type,
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
                        label=f"Mean Height of {event_type}",
                    )
                ]
            )

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

        percentage_opponent_half = round(100 * count_opponent_half / len(events), 2)
        ax.text(92.5, -2.1, "@francescozonaro", fontsize=10, va="center")
        ax.text(
            0,
            -2.1,
            f"Number of events: {len(events)}",
            fontsize=7,
            va="center",
            ha="left",
        )
        ax.text(
            0,
            -4.1,
            f"Percentage in opponent half: {percentage_opponent_half}%",
            fontsize=7,
            va="center",
            ha="left",
        )

        plt.savefig(f"imgs/{filename}.png", bbox_inches="tight", format="png", dpi=300)

    def draw(
        self,
        g,
        mode,
        marker_shape="o",
        marker_color=[(0.5, 0.78, 0.97, 1)],
    ):

        df_events = self.api.events(game_id=g, load_360=True)
        teams = list(df_events["team_name"].unique())
        team_ids = list(df_events["team_id"].unique())

        # COLORS
        if len(marker_color) == 0:
            raise ValueError("marker_color list cannot be empty.")
        elif len(marker_color) == len(team_ids):
            pass
        elif len(marker_color) > len(team_ids):
            marker_color = marker_color[:2]
        else:
            marker_color = marker_color * len(team_ids)

        for team_id, team, marker_color in zip(team_ids, teams, marker_color):

            opposing_team_id = next(t for t in team_ids if t != team_id)

            if mode == "defensive":
                types = [
                    "Block",
                    "Interception",
                    "Clearance",
                    "Ball Recovery",
                ]
                df = df_events[df_events["type_name"].isin(types)]
                df = df[df["team_id"] == team_id].reset_index(drop=True)
                # For this plot we consider only situations where an opponent has the ball
                df = df[df["possession_team_id"] == opposing_team_id]
                # Ignoring the keeper
                df = df[df["position_name"] != "Goalkeeper"]

                event_type_name = "Def. Action"
            elif mode == "passing":
                types = ["Pass"]
                df = df_events[df_events["type_name"].isin(types)]
                df = df[df["team_id"] == team_id].reset_index(drop=True)

                event_type_name = "Passing"
            else:
                raise ValueError(f"{mode} isn't supported")

            event_type = f"{team} {event_type_name}"
            filename = f"{g}_{team_id}_scatterplot_{event_type_name}"

            self._draw_event_type_scatter(
                df,
                filename=filename,
                event_type=event_type,
                draw_mean_height=True,
                marker_shape=marker_shape,
                marker_color=marker_color,
            )
