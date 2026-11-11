"""

Based on Sergio Llana (@SergioMinuto90) passing network created on Sun Apr 19 2020

Modified Jun 24 2023

@author: Francesco Zonaro

"""

import matplotlib.lines as mlines
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt

from statsbombplot.cli import game_args, resolve_game
from statsbombplot.config import (
    AWAY_TEAM_COLOR,
    FIG_BACKGROUND_COLOR,
    HOME_TEAM_COLOR,
    OUTPUT_DIR,
    PITCH_RATIO,
)
from statsbombplot.data import fetch_match
from statsbombplot.pitch import FullPitch
from statsbombplot.plotting import apply_style, save_figure

# Display names for the labels: the plot shows each player's last word, so multi-part surnames
# and long legal names are rewritten. Add entries here for other matches.
PLAYER_MAPPINGS = {
    "Emerson Palmieri dos Santos": "Emerson Palmieri",
    "Giovanni Di Lorenzo": "Giovanni DiLorenzo",
    "Jorge Luiz Frello Filho": "Jorginho",
}


def main():
    apply_style()
    args = game_args("Passing network of each team in a match.")
    game_id = resolve_game(args.game_id)
    match = fetch_match(game_id)
    for identifier, team_name, team_color in zip(
        match.team_ids, match.team_names, (HOME_TEAM_COLOR, AWAY_TEAM_COLOR)
    ):
        # Data
        df = match.events[match.events["team_id"] == identifier]
        id_first_sub = df[df.type_name == "Substitution"].index.min()
        is_before_first_sub = df.index < id_first_sub
        is_pass = df.type_name == "Pass"
        df = df[is_before_first_sub & is_pass]

        is_successful = df["extra"].apply(lambda x: "outcome" not in x["pass"])
        df = df[is_successful].reset_index(drop=True)

        df["pass_data"] = df["extra"].apply(lambda x: x.get("pass", {}))
        df["receiver"] = df["pass_data"].apply(lambda x: x.get("recipient", {}).get("name"))
        df["location_end"] = df["pass_data"].apply(lambda x: x.get("end_location"))

        df["player_name"] = df["player_name"].replace(PLAYER_MAPPINGS)
        df["receiver"] = df["receiver"].replace(PLAYER_MAPPINGS)
        df["pair_key"] = df.apply(
            lambda x: "_".join(sorted([x["player_name"], x["receiver"]])), axis=1
        )
        df[["x", "y"]] = df["location"].tolist()
        df[["x_end", "y_end"]] = df["location_end"].tolist()
        df["y"] = 80 - df["y"]
        df["y_end"] = 80 - df["y_end"]
        df = df[["player_name", "x", "y", "receiver", "x_end", "y_end", "pair_key"]]

        player_stats = df.groupby("player_name").agg(
            num_passes=("player_name", "size"),
            x=("x", "mean"),
            y=("y", "mean"),
        )
        pair_pass_count = df.groupby("pair_key").size().to_frame("num_passes")
        pair_pass_count = pair_pass_count[pair_pass_count["num_passes"] > 3]
        max_player_pass_count = player_stats.num_passes.max()
        max_pair_pass_count = pair_pass_count.num_passes.max()

        # Figure
        pitch = FullPitch()
        fig, ax = plt.subplots(1, 1, figsize=(15, 15 * PITCH_RATIO), dpi=300)
        ax.set_facecolor(FIG_BACKGROUND_COLOR)
        pitch.draw(ax)

        for pair_key, row in pair_pass_count.iterrows():
            player1, player2 = pair_key.split("_")
            player1_x = player_stats.loc[player1]["x"]
            player1_y = player_stats.loc[player1]["y"]
            player2_x = player_stats.loc[player2]["x"]
            player2_y = player_stats.loc[player2]["y"]

            num_passes = row["num_passes"]
            line_width = 3.5 * num_passes / max_pair_pass_count

            ax.plot(
                [player1_x, player2_x],
                [player1_y, player2_y],
                linestyle="-",
                alpha=0.4,
                lw=line_width,
                zorder=3,
                color=team_color,
            )

        for player_name, row in player_stats.iterrows():
            player_x = player_stats.loc[player_name]["x"]
            player_y = player_stats.loc[player_name]["y"]
            num_passes = row["num_passes"]
            marker_size = 100 * num_passes / max_player_pass_count

            ax.plot(
                player_x,
                player_y,
                ".",
                markersize=marker_size,
                color=team_color,
                zorder=5,
            )
            ax.plot(
                player_x,
                player_y,
                ".",
                markersize=marker_size - 15,
                color=FIG_BACKGROUND_COLOR,
                zorder=6,
            )
            ax.annotate(
                player_name.split()[-1],
                xy=(player_x, player_y),
                ha="center",
                va="center",
                zorder=7,
                weight="bold",
                size=8,
                path_effects=[pe.withStroke(linewidth=2, foreground="white")],
            )

        legend_elements = [
            plt.scatter(
                [],
                [],
                s=15,
                edgecolor=team_color,
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
                edgecolor=team_color,
                linewidth=2,
                facecolor=(1, 1, 1, 0.8),
                zorder=5,
                marker="o",
                label="Many passes made",
            ),
            mlines.Line2D(
                [],
                [],
                color=team_color,
                linewidth=1,
                linestyle="solid",
                label="Pair combines rarely",
            ),
            mlines.Line2D(
                [],
                [],
                color=team_color,
                linewidth=4,
                linestyle="solid",
                label="Pair combines frequently",
            ),
        ]

        extra_text = [
            "Player positions are based on the average locations from which passes were made.",
            "Only events occurring before the first substitution are included.",
        ]

        pitch.add_pitch_legend(ax, legend_elements)
        pitch.add_pitch_notes(
            ax,
            extra_text=extra_text,
        )
        fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)

        save_figure(fig, OUTPUT_DIR / "passing_networks" / f"{match.game_id}_{team_name}.png")


if __name__ == "__main__":
    main()
