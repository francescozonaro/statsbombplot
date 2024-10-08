import os
import matplotlib.pyplot as plt
from tqdm import tqdm
from utils import (
    getStatsbombAPI,
    fetchMatch,
)

api = getStatsbombAPI()
df = api.games(competition_id=55, season_id=43)
df = df[
    (df["home_team_name"].isin(["England", "Italy"]))
    | (df["away_team_name"].isin(["England", "Italy"]))
]
games = list(df["game_id"])
folder = os.path.join("imgs/", str(f"findBangers"))
load_360 = True
os.makedirs(folder, exist_ok=True)


class Banger:

    def __init__(
        self, playerName, teamName, opponentName, minute, xG, bodyPart, playType
    ):

        self.playerName = playerName
        playerParts = playerName.split()
        if len(playerParts) > 2:
            self.playerName = f"{playerParts[0]} {playerParts[-1]}"

        self.teamName = teamName
        teamParts = teamName.split()
        if len(teamParts) > 1:
            self.teamName = f"{teamParts[0]}"

        self.opponentName = opponentName
        opponentParts = opponentName.split()
        if len(opponentParts) > 1:
            self.opponentName = f"{opponentParts[0]}"

        self.xG = xG
        self.bodyPart = bodyPart
        self.playType = playType
        self.minute = minute


bangers = []

for gameId in tqdm(games, leave=False):
    match = fetchMatch(gameId, load_360)

    df = match.events
    shots = df[df["type_name"] == "Shot"]

    for i, row in shots.iterrows():
        if row["extra"]["shot"]["outcome"]["name"] == "Goal":

            teamName = row["team_name"]

            if teamName == match.homeTeamName:
                opponentName = match.awayTeamName
            else:
                opponentName = match.homeTeamName

            goalMinute = f"{row['minute']}:{row['second']:02d}"

            banger = Banger(
                playerName=row["player_name"],
                teamName=teamName,
                opponentName=opponentName,
                minute=goalMinute,
                xG=round(row["extra"]["shot"]["statsbomb_xg"], 3),
                bodyPart=row["extra"]["shot"]["body_part"]["name"],
                playType=row["extra"]["shot"]["type"]["name"],
            )
            bangers.append(banger)

plt.rcParams["font.family"] = "Arial"

fig = plt.figure(figsize=(10, 7), dpi=600)
ax = plt.subplot()

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_axis_off()

# Title
plt.text(
    x=0.05,
    y=1.1,
    s="Low xG goals from Italy/England matches in EURO 2020",
    va="center",
    ha="left",
    fontsize=18,
    color="black",
    weight="bold",
)
plt.text(
    x=0.05,
    y=1.15,
    s="   ",
    va="center",
    ha="left",
    fontsize=8,
    color="black",
    weight="bold",
)

plt.rcParams["font.family"] = "Menlo"

plt.text(
    x=0.05,
    y=1.025,
    s="A collection of goals with the lowest xG scored in matches featuring England and Italy\nthroughout their journey to the EURO 2020 final.",
    va="center",
    ha="left",
    fontsize=9,
    color="#4E616C",
)

# Cols
ax.text(
    x=0.66,
    y=0.95,
    s="SHOT xG",
    size=9,
    ha="center",
    va="center",
    weight="extra bold",
)
ax.text(
    x=0.78,
    y=0.95,
    s="BODY PART",
    size=9,
    ha="center",
    va="center",
    weight="extra bold",
)
ax.text(
    x=0.9,
    y=0.95,
    s="PLAY TYPE",
    size=9,
    ha="center",
    va="center",
    weight="extra bold",
)

# Lines
ax.plot(
    [0.05, 0.95],
    [0.9, 0.9],
    lw=0.7,
    color="black",
    zorder=3,
)
ax.plot(
    [0.05, 0.95],
    [0.1, 0.1],
    lw=0.7,
    color="black",
    zorder=3,
)

filteredBangers = filter(
    lambda b: (b.teamName == "Italy" or b.teamName == "England"), bangers
)
sortedBangers = sorted(bangers, key=lambda b: b.xG)
bangersList = sortedBangers[0:8]

for i, banger in enumerate(bangersList):
    rowHeight = 1 - 0.15 - i * 0.1

    if i % 2 == 0:
        ax.fill_between(
            x=[0.05, 0.95],
            y1=rowHeight - 0.05,
            y2=rowHeight + 0.05,
            color="#d7c8c1",
            zorder=-1,
        )

    ax.text(
        x=0.06,
        y=rowHeight,
        s=f"{banger.playerName}",
        weight="bold",
        size=9,
        ha="left",
        va="center",
    )
    ax.text(
        x=0.3,
        y=rowHeight,
        s=f"{banger.teamName} vs {banger.opponentName} ({banger.minute})",
        weight="bold",
        size=9,
        ha="left",
        va="center",
    )
    ax.text(
        x=0.66,
        y=rowHeight,
        s=f"{banger.xG}",
        size=9,
        ha="center",
        va="center",
    )
    ax.text(
        x=0.78,
        y=rowHeight,
        s=f"{banger.bodyPart}",
        size=9,
        ha="center",
        va="center",
    )
    ax.text(
        x=0.9,
        y=rowHeight,
        s=f"{banger.playType}",
        size=9,
        ha="center",
        va="center",
    )

ax.text(
    x=0.05,
    y=0.03,
    s=f"Data from Opta as of 7th October 2024",
    size=7,
    ha="left",
    va="center",
)
ax.text(
    x=0.95,
    y=0.03,
    s=f"@francescozonaro",
    size=7,
    ha="right",
    va="center",
)


plt.savefig(
    f"{folder}/test.png",
    dpi=600,
    facecolor="#EFE9E6",
    bbox_inches="tight",
    edgecolor="none",
    transparent=False,
)
