import os
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patheffects as pe

from utils import (
    Pitch,
    getStatsbombAPI,
    addLegend,
    addNotes,
    saveFigure,
    fetchMatch,
)

api = getStatsbombAPI()
df = api.games(competition_id=55, season_id=282)
print(df.columns)
df = df[df[["home_team_name", "away_team_name"]].isin(["France"]).any(axis=1)]
games = list(df["game_id"])

for gameId in games:

    load_360 = True
    folder = os.path.join("imgs/", str(gameId))
    match = fetchMatch(gameId, load_360)
    os.makedirs(folder, exist_ok=True)

    df = match.events
    passes = df[df["type_name"] == "Pass"]
    passes = passes[passes["player_name"] == "Mike Maignan"]
    # passes = passes.dropna(subset=["freeze_frame_360"])

    mainColor = match.awayTeamColor
    oppColor = match.homeTeamColor

    plt.close()
    pitch = Pitch()
    f, ax = pitch.draw()

    for i, row in passes.iterrows():

        x = row.location[0]
        y = 80 - row.location[1]
        end_x = row["extra"]["pass"]["end_location"][0]
        end_y = 80 - row["extra"]["pass"]["end_location"][1]

        ax.scatter(
            x,
            y,
            s=150,
            edgecolor="black",
            linewidth=0.6,
            facecolor="#669bbc",
            zorder=9,
            marker="o",
        )

        if row["under_pressure"]:
            lineColor = "#588157"
        else:
            lineColor = "#e5e5e5"

        if "outcome" in row["extra"]["pass"]:
            lineColor = "#f4978e"

        ax.plot(
            [x, end_x],
            [y, end_y],
            color=lineColor,
            linewidth=1.5,
            zorder=5,
            linestyle="-",
        )

    legendElements = [
        plt.scatter(
            [],
            [],
            s=70,
            edgecolor="black",
            linewidth=0.6,
            facecolor="#669bbc",
            zorder=5,
            marker="o",
            label="Maignan",
        ),
        mlines.Line2D(
            [],
            [],
            color="#d3d3d3",
            linewidth=3,
            linestyle="solid",
            label=f"Generic",
        ),
        mlines.Line2D(
            [],
            [],
            color="#e76f51",
            linewidth=3,
            linestyle="solid",
            label=f"Incomplete",
        ),
        mlines.Line2D(
            [],
            [],
            color="#588157",
            linewidth=3,
            linestyle="solid",
            label=f"Under press",
        ),
    ]

    extra = [f"{match.homeTeamName} vs {match.awayTeamName}"]
    addLegend(ax, legendElements=legendElements)
    addNotes(ax, extra_text=extra, author="@francescozonaro")
    saveFigure(f, f"{folder}/360pass_{match.gameId}.png")
