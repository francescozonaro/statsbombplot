import os
import matplotlib.pyplot as plt
from tqdm import tqdm
from utils import (
    getStatsbombAPI,
    fetchMatch,
)
from datetime import datetime

api = getStatsbombAPI()
df = api.games(competition_id=43, season_id=106)  # or 3
competitionName = df["competition_name"].iloc[0]
seasonName = df["season_name"].iloc[0]
games = list(df["game_id"])
folder = os.path.join("imgs/", str(f"goalsWorthWatching"))
load_360 = True
os.makedirs(folder, exist_ok=True)


class Banger:

    def __init__(
        self,
        playerName,
        teamName,
        opponentName,
        minute,
        xG,
        location,
        endLocation,
        technique,
        bodyPart,
        playType,
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
        self.location = location
        self.endLocation = endLocation
        self.technique = technique
        self.bodyPart = bodyPart
        self.playType = playType
        self.minute = minute

        xBanger = 1 - self.xG

        if self.technique != "Normal":
            xBanger += 0.05

        distance = ((40 - endLocation[1]) ** 2 + (0 - endLocation[2] * 2) ** 2) ** 0.5

        if distance > 5:
            xBanger += 0.075

        self.xBanger = round(xBanger, 2)


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
                location=row["location"],
                endLocation=row["extra"]["shot"]["end_location"],
                technique=row["extra"]["shot"]["technique"]["name"],
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
    s=f"GOALS WORTH WATCHING | {competitionName} {seasonName} Edition",
    va="center",
    ha="left",
    fontsize=17,
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

# Subtitle
plt.text(
    x=0.05,
    y=1.025,
    s=f"Remarkable goals from {competitionName} {seasonName}, selected for their exceptional xG values,\nstriking technique and precise placement, making them well worth revisiting.",
    va="center",
    ha="left",
    fontsize=9,
    color="#4E616C",
)

# Cols
ax.text(
    x=0.66,
    y=0.95,
    s="xBanger",
    size=9,
    ha="center",
    va="center",
    weight="extra bold",
)
ax.text(
    x=0.78,
    y=0.95,
    s="TECHNIQUE",
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

sortedBangers = sorted(bangers, key=lambda b: b.xBanger, reverse=True)
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
        s=f"{banger.xBanger}",
        size=9,
        ha="center",
        va="center",
    )
    ax.text(
        x=0.78,
        y=rowHeight,
        s=f"{banger.technique}",
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
    s=f"Data from Opta as of {datetime.now().strftime('%d %B %Y')}",
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
    f"{folder}/table.png",
    dpi=600,
    facecolor="#EFE9E6",
    bbox_inches="tight",
    edgecolor="none",
    transparent=False,
)
