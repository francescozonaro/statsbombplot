import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import os
import json

from utils import Pitch, getStatsbombAPI, addLegend, addNotes, saveFigure, fetchMatch


class ShotFrame:

    def __init__(self, homeColor, awayColor, nameMapping):
        self.homeColor = homeColor
        self.awayColor = awayColor
        self.nameMapping = nameMapping

    def draw(self, x, y, end_x, end_y, frame, isHome):

        pitch = Pitch()
        f, ax = pitch.draw()

        if isHome:
            mainColor = self.homeColor
            oppColor = self.awayColor
        else:
            mainColor = self.awayColor
            oppColor = self.homeColor

        ax.scatter(
            x,
            y,
            s=120,
            edgecolor="black",
            linewidth=0.6,
            facecolor=mainColor,
            zorder=11,
            marker="*",
        )

        ax.plot(
            [x, end_x],
            [y, end_y],
            color=(0, 0, 0, 0.2),
            linewidth=0.9,
            zorder=5,
            linestyle="--",
        )

        for player in frame:

            freezed_player_x = player["location"][0]
            freezed_player_y = 80 - player["location"][1]

            if player["teammate"]:
                freezed_player_color = mainColor
            else:
                freezed_player_color = oppColor

            ax.scatter(
                freezed_player_x,
                freezed_player_y,
                s=120,
                edgecolor="black",
                linewidth=0.6,
                facecolor=freezed_player_color,
                zorder=9,
                marker="o",
            )

            ax.text(
                freezed_player_x + 0.025,
                freezed_player_y - 0.05,
                f"{self.nameMapping[player['player']['name']]}",
                fontsize=6,
                zorder=9,
                ha="center",
                va="center",
                color="white",
                path_effects=[pe.withStroke(linewidth=1.5, foreground="black")],
            )

        legendElements = [
            plt.scatter(
                [],
                [],
                s=90,
                edgecolor="black",
                linewidth=0.6,
                facecolor=mainColor,
                zorder=5,
                marker="*",
                label="Shot location",
            ),
            plt.scatter(
                [],
                [],
                s=60,
                edgecolor="black",
                linewidth=0.6,
                facecolor=mainColor,
                zorder=5,
                marker="o",
                label="Teammate",
            ),
            plt.scatter(
                [],
                [],
                s=60,
                edgecolor="black",
                linewidth=0.6,
                facecolor=oppColor,
                zorder=5,
                marker="o",
                label="Opponent",
            ),
        ]

        plt.close()
        return f, ax, legendElements


with open("config.json", "r") as f:
    config = json.load(f)

gameId = config.get("gameId")
load_360 = config.get("load_360", True)
folder = os.path.join(config.get("folder", "imgs/"), str(gameId))
match = fetchMatch(gameId, load_360)
os.makedirs(folder, exist_ok=True)


playerNameToJerseyNumber = match.players.set_index("player_name")[
    "jersey_number"
].to_dict()

shotFrame = ShotFrame(
    match.homeTeamColor, match.awayTeamColor, playerNameToJerseyNumber
)

shots = match.events[match.events["type_name"] == "Shot"].reset_index(drop=True)

for i, shot in shots.iterrows():
    if shot.team_id == match.homeTeamId:
        isHome = True
    else:
        isHome = False

    if shot["period_id"] < 5:
        if (
            "extra" in shot
            and "shot" in shot["extra"]
            and "freeze_frame" in shot["extra"]["shot"]
        ):

            fig, ax, legendElements = shotFrame.draw(
                shot.location[0],
                80 - shot.location[1],
                shot["extra"]["shot"]["end_location"][0],
                80 - shot["extra"]["shot"]["end_location"][1],
                shot["extra"]["shot"]["freeze_frame"],
                isHome,
            )

            shotOutcome = shot.extra["shot"]["outcome"]["name"].lower()
            shotTechnique = shot.extra["shot"]["technique"]["name"].lower()
            shotValue = shot.extra["shot"]["statsbomb_xg"]

            if shotTechnique == "normal":
                shotTechnique = shot.extra["shot"]["body_part"]["name"].lower()

            extra = [
                f"{shot.player_name} shot at {shot.minute}:{shot.second} with {shotTechnique} had an xG of {round(shotValue, 3)} and resulted in {shotOutcome}"
            ]
            addLegend(ax, legendElements)
            addNotes(ax, author="@francescozonaro", extra_text=extra)
            saveFigure(fig, f"{folder}/shotFreezed_{match.gameId}_{i}.png")
        else:
            print(f"Skipping shot {i}: 'freeze_frame' not available.")
    else:
        print(f"Skipping shot {i}: Penalty shots are excluded.")
