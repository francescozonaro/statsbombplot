"""

Based on Sergio Llana (@SergioMinuto90) passing network created on Sun Apr 19 2020

Modified Jun 24 2023

@author: Francesco Zonaro

"""

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import os

from utils.fullPitch import FullPitch
from utils.commons import saveFigure, fetchMatch
from utils.config import *

folder = os.path.join("imgs/", str(f"passingNetwork"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

GAME_ID = 3795506  # EURO 2020 Final
TEAM_COLORS = ["#3f8ae6", "#f04a5f"]
PLAYER_MAPPINGS = {
    "Emerson Palmieri dos Santos": "Emerson Palmieri",
    "Giovanni Di Lorenzo": "Giovanni DiLorenzo",
    "Jorge Luiz Frello Filho": "Jorginho",
}

match = fetchMatch(GAME_ID, load_360=True)
for identifier, teamName, teamColor in zip(
    match.teamIdentifiers, match.teamNames, TEAM_COLORS
):
    # Data
    df = match.events[match.events["team_id"] == identifier]
    idFirstSub = df[df.type_name == "Substitution"].index.min()
    isBeforeFirstSub = df.index < idFirstSub
    isPass = df.type_name == "Pass"
    df = df[isBeforeFirstSub & isPass]

    isSuccessful = df["extra"].apply(lambda x: "outcome" not in x["pass"])
    df = df[isSuccessful].reset_index(drop=True)

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

    playerStats = df.groupby("player_name").agg(
        num_passes=("player_name", "size"),
        x=("x", "mean"),
        y=("y", "mean"),
    )
    pairPassCount = df.groupby("pair_key").size().to_frame("num_passes")
    pairPassCount = pairPassCount[pairPassCount["num_passes"] > 3]
    maxPlayerPassCount = playerStats.num_passes.max()
    maxPairPassCount = pairPassCount.num_passes.max()

    # Figure
    pitch = FullPitch()
    fig, ax = plt.subplots(1, 1, figsize=(15, 15 * PITCH_RATIO), dpi=300)
    ax.set_facecolor(FIG_BACKGROUND_COLOR)
    pitch.draw(ax)

    for pair_key, row in pairPassCount.iterrows():
        player1, player2 = pair_key.split("_")
        player1_x = playerStats.loc[player1]["x"]
        player1_y = playerStats.loc[player1]["y"]
        player2_x = playerStats.loc[player2]["x"]
        player2_y = playerStats.loc[player2]["y"]

        numPasses = row["num_passes"]
        lineWidth = 3.5 * numPasses / maxPairPassCount

        ax.plot(
            [player1_x, player2_x],
            [player1_y, player2_y],
            linestyle="-",
            alpha=0.4,
            lw=lineWidth,
            zorder=3,
            color=teamColor,
        )

    for playerName, row in playerStats.iterrows():
        playerX = playerStats.loc[playerName]["x"]
        playerY = playerStats.loc[playerName]["y"]
        numPasses = row["num_passes"]
        markerSize = 100 * numPasses / maxPlayerPassCount

        ax.plot(
            playerX,
            playerY,
            ".",
            markersize=markerSize,
            color=teamColor,
            zorder=5,
        )
        ax.plot(
            playerX,
            playerY,
            ".",
            markersize=markerSize - 15,
            color=FIG_BACKGROUND_COLOR,
            zorder=6,
        )
        ax.annotate(
            playerName.split()[-1],
            xy=(playerX, playerY),
            ha="center",
            va="center",
            zorder=7,
            weight="bold",
            size=8,
            path_effects=[pe.withStroke(linewidth=2, foreground="white")],
        )

    legendElements = [
        plt.scatter(
            [],
            [],
            s=15,
            edgecolor=teamColor,
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
            edgecolor=teamColor,
            linewidth=2,
            facecolor=(1, 1, 1, 0.8),
            zorder=5,
            marker="o",
            label="Many passes made",
        ),
        mlines.Line2D(
            [],
            [],
            color=teamColor,
            linewidth=1,
            linestyle="solid",
            label=f"Pair combines rarely",
        ),
        mlines.Line2D(
            [],
            [],
            color=teamColor,
            linewidth=4,
            linestyle="solid",
            label=f"Pair combines frequently",
        ),
    ]

    extra_text = [
        "Player positions are based on the average locations from which passes were made.",
        "Only events occurring before the first substitution are included.",
    ]

    pitch.addPitchLegend(ax, legendElements)
    pitch.addPitchNotes(
        ax,
        extra_text=extra_text,
    )
    fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)

    saveFigure(fig, f"{folder}/{match.gameId}_{teamName}.png")
