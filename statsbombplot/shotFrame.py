import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import os

from utils import (
    FullPitch,
    saveFigure,
    fetchRandomMatch,
)


match = fetchRandomMatch(seed=602210)
folder = os.path.join("imgs/", str(match.gameId))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

homeTeamColor = "#3f8ae6"
awayTeamColor = "#f04a5f"
playerNameToJerseyNumber = {
    player["player_name"]: player["jersey_number"]
    for _, player in match.players.iterrows()
}

df = match.events
isShot = df["type_name"] == "Shot"
isValidPeriod = df["period_id"] < 5
hasFreezeFrame = df["extra"].apply(
    lambda x: isinstance(x, dict)
    and "shot" in x
    and "freeze_frame" in x.get("shot", {})
)

validShots = df[isShot & isValidPeriod & hasFreezeFrame].reset_index(drop=True)

for i, shot in validShots.iterrows():

    isHome = shot.team_id == match.homeTeamId
    pitch = FullPitch()

    fig, ax = plt.subplots(1, 1, figsize=(15, 15 * (80 / 120)), dpi=300)
    pitch.draw(ax)

    x = shot.location[0]
    y = 80 - shot.location[1]
    end_x = shot["extra"]["shot"]["end_location"][0]
    end_y = 80 - shot["extra"]["shot"]["end_location"][1]
    frame = shot["extra"]["shot"]["freeze_frame"]

    if isHome:
        mainColor = homeTeamColor
        oppColor = awayTeamColor
    else:
        mainColor = awayTeamColor
        oppColor = homeTeamColor

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
            f"{playerNameToJerseyNumber[player['player']['name']]}",
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

    shotOutcome = shot.extra["shot"]["outcome"]["name"].lower()
    shotTechnique = (
        shot.extra["shot"]["body_part"]["name"].lower()
        if shot.extra["shot"]["technique"]["name"].lower() == "normal"
        else shot.extra["shot"]["technique"]["name"].lower()
    )
    shotValue = shot.extra["shot"]["statsbomb_xg"]

    formattedTime = f"{shot.minute}:{shot.second:02d}"
    extra = [
        f"At {formattedTime}, {shot.player_name} took a shot with {shotTechnique}, had an xG of {round(shotValue, 3)}, and it resulted in {shotOutcome}."
    ]

    pitch.addPitchLegend(ax, legendElements)
    pitch.addPitchNotes(ax, author="@francescozonaro", extra_text=extra)
    saveFigure(fig, f"{folder}/shotFreezed_{match.gameId}_{i}.png")

    plt.close()
    exit()
