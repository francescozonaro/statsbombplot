import matplotlib.pyplot as plt
from utils import config, draw_pitch, change_range
import matplotlib.lines as mlines
import numpy as np


def is_progressive(x, y, end_x, end_y):
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


def draw_progressive_events(events, title, filename, drawAttempted, toggleTimestamp):
    figsize_ratio = config["fig_size"] / 12
    ax = draw_pitch()

    events["end_location"] = events["extra"].apply(
        lambda x: (
            x["carry"]["end_location"] if "carry" in x else x["pass"]["end_location"]
        )
    )

    for i, event in events.iterrows():
        markersize = 50 * figsize_ratio
        linewidth = 0.5 * figsize_ratio
        fontsize = 6 * figsize_ratio

        # Statsbomb pitch dimensions: 120 length, 80 width. My pitch dimensions: 105 length, 68 width.

        x = change_range(event.location[0], [0, 120], [0, 105])
        y = 68 - change_range(event.location[1], [0, 80], [0, 68])
        x_end = change_range(event.end_location[0], [0, 120], [0, 105])
        y_end = 68 - change_range(event.end_location[1], [0, 80], [0, 68])

        if event.type_name == "Carry":
            if is_progressive(x, y, x_end, y_end):
                ax.scatter(
                    x,
                    y,
                    s=markersize,
                    edgecolor="black",
                    linewidth=linewidth,
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
                        fontsize=fontsize,
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
            if is_progressive(x, y, x_end, y_end):
                ax.scatter(
                    x,
                    y,
                    s=markersize,
                    edgecolor="black",
                    linewidth=linewidth,
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
                        fontsize=fontsize,
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
            s=markersize,
            edgecolor="black",
            linewidth=linewidth,
            facecolor="#f4a261",
            zorder=7,
            marker="o",
            label="Progressive Carry",
        ),
        plt.scatter(
            [],
            [],
            s=markersize,
            edgecolor="black",
            linewidth=linewidth,
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

    ax.text(1, 66, f"{title}", fontsize=10, va="center", ha="left")
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


import os
import warnings
import sys
from statsbombpy.api_client import NoAuthWarning
from socceraction.data.statsbomb import StatsBombLoader

warnings.simplefilter("ignore", NoAuthWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
api = StatsBombLoader(getter="remote", creds={"user": "", "passwd": ""})

g = 3795506
df_teams = api.teams(game_id=g)
df_players = api.players(game_id=g)
df_events = api.events(game_id=g, load_360=True)
teams = list(df_events["team_name"].unique())
teams_id = list(df_events["team_id"].unique())

draw_id = 0
types = ["Pass", "Carry"]
df = df_events[df_events["type_name"].isin(types)]
df = df[df["player_name"] == "Federico Chiesa"].reset_index(
    drop=True
)  # Consider only one player for the sake of tidiness

draw_progressive_events(
    df,
    "Federico Chiesa",
    "chiesaProgressive",
    drawAttempted=False,
    toggleTimestamp=True,
)
