import matplotlib.patheffects as pe
import pandas as pd
from statsbombplot.utils import config, draw_pitch, change_range
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


def draw_passing_network(df, filename, marker_color):
    df[["x", "y"]] = pd.DataFrame(df["location"].tolist())
    df[["x_end", "y_end"]] = pd.DataFrame(df["location_end"].tolist())

    df["x"] = df["x"].apply(lambda value: change_range(value, [0, 120], [0, 105]))
    df["y"] = 68 - df["y"].apply(lambda value: change_range(value, [0, 80], [0, 68]))
    df["x_end"] = df["x_end"].apply(
        lambda value: change_range(value, [0, 120], [0, 105])
    )
    df["y_end"] = df["y_end"].apply(lambda value: change_range(value, [0, 80], [0, 68]))

    df = df[["player_name", "x", "y", "receiver", "x_end", "y_end"]]

    player_pass_count = df.groupby("player_name").size().to_frame("num_passes")

    df["pair_key"] = df.apply(
        lambda x: "_".join(sorted([x["player_name"], x["receiver"]])), axis=1
    )

    pair_pass_count = df.groupby("pair_key").size().to_frame("num_passes")
    pair_pass_count = pair_pass_count[pair_pass_count["num_passes"] > 3]
    player_position = df.groupby("player_name").agg({"x": "mean", "y": "mean"})

    figsize_ratio = config["fig_size"] / 12
    ax = draw_pitch()

    max_player_count = player_pass_count.num_passes.max()
    max_pair_count = pair_pass_count.num_passes.max()

    for pair_key, row in pair_pass_count.iterrows():
        player1, player2 = pair_key.split("_")
        player1_x = player_position.loc[player1]["x"]
        player1_y = player_position.loc[player1]["y"]
        player2_x = player_position.loc[player2]["x"]
        player2_y = player_position.loc[player2]["y"]

        num_passes = row["num_passes"]
        line_width = num_passes / max_pair_count
        ax.plot(
            [player1_x, player2_x],
            [player1_y, player2_y],
            linestyle="-",
            alpha=0.4,
            lw=2.5 * line_width * figsize_ratio,
            zorder=3,
            color=marker_color,
        )

    for player_name, row in player_pass_count.iterrows():
        player_x = player_position.loc[player_name]["x"]
        player_y = player_position.loc[player_name]["y"]
        num_passes = row["num_passes"]
        marker_size = num_passes / max_player_count

        ax.plot(
            player_x,
            player_y,
            ".",
            markersize=100 * (marker_size) * figsize_ratio,
            color=marker_color,
            zorder=5,
        )
        ax.plot(
            player_x,
            player_y,
            ".",
            markersize=100 * (marker_size) * figsize_ratio
            - 15 * (marker_size) * figsize_ratio,
            color="white",
            zorder=6,
        )
        ax.annotate(
            player_name.split()[-1],
            xy=(player_x, player_y),
            ha="center",
            va="center",
            zorder=7,
            weight="bold",
            size=8 * figsize_ratio,
            path_effects=[pe.withStroke(linewidth=2, foreground="white")],
        )

    legend_elements = [
        plt.scatter(
            [],
            [],
            s=15,
            edgecolor=marker_color,
            linewidth=1,
            facecolor=(1, 1, 1, 0.8),
            zorder=5,
            marker="o",
            label="Few passes made",
        ),
        plt.scatter(
            [],
            [],
            s=150,
            edgecolor=marker_color,
            linewidth=2,
            facecolor=(1, 1, 1, 0.8),
            zorder=5,
            marker="o",
            label="Many passes made",
        ),
        mlines.Line2D(
            [],
            [],
            color=marker_color,
            linewidth=1,
            linestyle="solid",
            label=f"Pair combines rarely",
        ),
        mlines.Line2D(
            [],
            [],
            color=marker_color,
            linewidth=4,
            linestyle="solid",
            label=f"Pair combines frequently",
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
        0,
        -2.1,
        f"Player position is the mean location in which they passed the ball",
        fontsize=7,
        va="center",
        ha="left",
    )
    ax.text(
        0,
        -4.1,
        f"Only events before the first substitution are considered",
        fontsize=7,
        va="center",
        ha="left",
    )

    plt.savefig(f"imgs/{filename}.png", bbox_inches="tight", format="png", dpi=300)
