import os
import matplotlib.pyplot as plt
from tqdm import tqdm
from utils import (
    getStatsbombAPI,
    fetchMatch,
)

api = getStatsbombAPI()
df = api.games(competition_id=55, season_id=43)
games = list(df["game_id"])
folder = os.path.join("imgs/", str(f"findBangers"))
load_360 = True
os.makedirs(folder, exist_ok=True)


class Banger:

    def __init__(self, playerName, teamName, xG, bodyPart, playType):

        self.playerName = playerName
        playerParts = playerName.split()
        if len(playerParts) > 2:
            self.playerName = f"{playerParts[0]} {playerParts[-1]}"

        self.teamName = teamName
        teamParts = teamName.split()
        if len(teamParts) > 1:
            self.teamName = f"{teamParts[0]}"

        self.xG = xG
        self.bodyPart = bodyPart
        self.playType = playType


bangers = []

for gameId in tqdm(games, leave=False):
    match = fetchMatch(gameId, load_360)
    df = match.events
    shots = df[df["type_name"] == "Shot"]

    for i, row in shots.iterrows():
        if row["extra"]["shot"]["statsbomb_xg"] < 0.1:
            if row["extra"]["shot"]["outcome"]["name"] == "Goal":

                banger = Banger(
                    playerName=row["player_name"],
                    teamName=row["team_name"],
                    xG=round(row["extra"]["shot"]["statsbomb_xg"], 3),
                    bodyPart=row["extra"]["shot"]["body_part"]["name"],
                    playType=row["extra"]["shot"]["type"]["name"],
                )
                bangers.append(banger)

fig = plt.figure(figsize=(7, 10), dpi=600)
ax = plt.subplot()

nrows = len(bangers)
ncols = 7

ax.set_xlim(0, ncols + 1)
ax.set_ylim(-0.65, nrows + 1)

for y, banger in enumerate(bangers):
    ax.text(
        x=0.15,
        y=y,
        s=f"{banger.playerName}",
        weight="bold",
        size=9,
        ha="left",
        va="center",
    )
    ax.text(
        x=3.15,
        y=y,
        s=f"{banger.teamName}",
        weight="bold",
        size=9,
        ha="center",
        va="center",
    )
    ax.text(
        x=4.65,
        y=y,
        s=f"{banger.xG}",
        size=9,
        ha="center",
        va="center",
    )
    ax.text(
        x=6.15,
        y=y,
        s=f"{banger.bodyPart}",
        size=9,
        ha="center",
        va="center",
    )
    ax.text(
        x=7.65,
        y=y,
        s=f"{banger.playType}",
        size=9,
        ha="center",
        va="center",
    )

ax.plot(
    [ax.get_xlim()[0], ax.get_xlim()[1]],
    [nrows - 0.5, nrows - 0.5],
    lw=1,
    color="black",
    zorder=3,
)
ax.plot(
    [ax.get_xlim()[0], ax.get_xlim()[1]], [-0.5, -0.5], lw=1, color="black", zorder=3
)

for x in range(nrows):
    if x % 2 == 0:
        ax.fill_between(
            x=[ax.get_xlim()[0], ax.get_xlim()[1]],
            y1=x - 0.5,
            y2=x + 0.5,
            color="#d7c8c1",
            zorder=-1,
        )
    ax.plot(
        [ax.get_xlim()[0], ax.get_xlim()[1]],
        [x - 0.5, x - 0.5],
        lw=1,
        color="grey",
        ls=":",
        zorder=3,
    )

ax.set_axis_off()
ax.text(
    x=4.65,
    y=nrows + 0.05,
    s="SHOT xG",
    size=9,
    ha="center",
    va="center",
    weight="bold",
)
ax.text(
    x=6.15,
    y=nrows + 0.05,
    s="BODY PART",
    size=9,
    ha="center",
    va="center",
    weight="bold",
)
ax.text(
    x=7.65,
    y=nrows + 0.05,
    s="PLAY TYPE",
    size=9,
    ha="center",
    va="center",
    weight="bold",
)

fig.text(
    x=0.15,
    y=0.92,
    s="EURO2020 BANGERS GOALS COLLECTION",
    va="bottom",
    ha="left",
    fontsize=14,
    color="black",
    weight="bold",
)
fig.text(
    x=0.15,
    y=0.87,
    s="Players in the top 85th percentile of crosses attempted & at least 1,000 minutes played.\nSeason 2022/2023 | viz by @sonofacorner.\nData from Opta as of 9th of January 2023",
    va="bottom",
    ha="left",
    fontsize=7,
    color="#4E616C",
)

plt.savefig(
    f"{folder}/test.png",
    dpi=600,
    facecolor="#EFE9E6",
    bbox_inches="tight",
    edgecolor="none",
    transparent=False,
)
