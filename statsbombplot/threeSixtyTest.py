import os
import json
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

from utils import Pitch, getStatsbombAPI, addLegend, addNotes, saveFigure, fetchMatch


gameId = 3795506
load_360 = True
folder = os.path.join("imgs/", str(gameId))
match = fetchMatch(gameId, load_360)
os.makedirs(folder, exist_ok=True)


df = match.events
df = df[df["type_name"] == "Pass"]
df = df[df["player_name"] == "Gianluigi Donnarumma"]
df = df.dropna(subset=["freeze_frame_360"])

mainColor = match.awayTeamColor
oppColor = match.homeTeamColor

for i, row in df.iterrows():

    pitch = Pitch()
    f, ax = pitch.draw()

    for player in row["freeze_frame_360"]:

        freezedPlayerX = player["location"][0]
        freezedPlayerY = 80 - player["location"][1]

        if player["teammate"]:
            freezedPlayerColor = mainColor
        else:
            freezedPlayerColor = oppColor

        freezedPlayerMarker = "d" if player["actor"] else "o"

        ax.scatter(
            freezedPlayerX,
            freezedPlayerY,
            s=150,
            edgecolor="black",
            linewidth=0.6,
            facecolor=freezedPlayerColor,
            zorder=9,
            marker=freezedPlayerMarker,
        )

    # addLegend(ax, [])
    addNotes(ax, author="@francescozonaro")
    saveFigure(f, f"{folder}/360pass_{match.gameId}_{i}.png")
