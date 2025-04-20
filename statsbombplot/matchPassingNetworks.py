"""

Based on Sergio Llana (@SergioMinuto90) passing network created on Sun Apr 19 2020

Modified Jun 24 2023

@author: Francesco Zonaro

"""

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import pandas as pd
import os

from utils import FullPitch, saveFigure, fetchMatch

folder = os.path.join("imgs/", str(f"passingNetwork"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"


GAME_ID = 3795506  # EURO 2020 Final
match = fetchMatch(GAME_ID, load_360=True)
teamColors = ["#3f8ae6", "#f04a5f"]

for identifier, teamName, teamColor in zip(
    match.teamIdentifiers, match.teamNames, teamColors
):
    teamEvents = match.events[match.events["team_id"] == identifier].copy()
    idFirstSub = teamEvents[teamEvents.type_name == "Substitution"].index.min()

    df = (
        teamEvents[
            (teamEvents.index < idFirstSub)
            & (teamEvents.type_name == "Pass")
            & (
                ~teamEvents["extra"].apply(
                    lambda x: "pass" in x and "outcome" in x["pass"]
                )
            )
        ]
        .copy()
        .reset_index(drop=True)
    )
    df["receiver"] = df["extra"].apply(
        lambda x: x.get("pass", {}).get("recipient", {}).get("name")
    )
    df["pair_key"] = df.apply(
        lambda x: "_".join(sorted([x["player_name"], x["receiver"]])), axis=1
    )
    df["location_end"] = df["extra"].apply(
        lambda x: x.get("pass", {}).get("end_location")
    )
    df[["x", "y"]] = pd.DataFrame(df["location"].tolist())
    df[["x_end", "y_end"]] = pd.DataFrame(df["location_end"].tolist())
    df["y"] = 80 - df["y"]

    df = df[["player_name", "x", "y", "receiver", "x_end", "y_end", "pair_key"]]

    playerPassCount = df.groupby("player_name").size().to_frame("num_passes")
    playerPosition = df.groupby("player_name").agg({"x": "mean", "y": "mean"})
    pairPassCount = df.groupby("pair_key").size().to_frame("num_passes")
    pairPassCount = pairPassCount[pairPassCount["num_passes"] > 3]
    maxPlayerPassCount = playerPassCount.num_passes.max()
    maxPairPassCount = pairPassCount.num_passes.max()

    pitch = FullPitch()
    fig, ax = pitch.draw()

    for pair_key, row in pairPassCount.iterrows():
        player1, player2 = pair_key.split("_")
        player1_x = playerPosition.loc[player1]["x"]
        player1_y = playerPosition.loc[player1]["y"]
        player2_x = playerPosition.loc[player2]["x"]
        player2_y = playerPosition.loc[player2]["y"]

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

    for playerName, row in playerPassCount.iterrows():
        playerX = playerPosition.loc[playerName]["x"]
        playerY = playerPosition.loc[playerName]["y"]
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
            color="white",
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
        author="@francescozonaro",
        extra_text=extra_text,
    )
    saveFigure(fig, f"{folder}/{match.gameId}_{teamName}.png")
