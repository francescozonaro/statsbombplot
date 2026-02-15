import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import os
import numpy as np
import urllib.request
import pandas as pd

from PIL import Image
from math import ceil
from matplotlib.patches import Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from tqdm import tqdm
from utils import (
    getAllTeamMatchesFromSeason,
    getCompetitionTeamNames,
    fetchMatch,
    saveFigure,
    FullPitch,
)


def findPlayerNameByRole(df, team, role):
    startingXI = df[
        (df["type_name"] == "Starting XI") & (df["team_name"] == team)
    ].iloc[0]
    lineup = startingXI["extra"]["tactics"]["lineup"]
    candidate = next(player for player in lineup if player["position"]["name"] == role)
    return candidate["player"]["name"]


folder = os.path.join("imgs/", str(f"goalkeeperPasses"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

NORMALIZE_DATA = False
COMPETITION_ID = 2
SEASON_ID = 27
RECTANGLE_COLOR_HEX = "#5668a4"
EDGE_COLOR_HEX = "#535353"
FOTMOB_URL = "https://images.fotmob.com/image_resources/logo/teamlogo/"
TEAM_LOGO_URL = {
    "AFC Bournemouth": f"{FOTMOB_URL}8678.png",
    "Arsenal": f"{FOTMOB_URL}9825.png",
    "Aston Villa": f"{FOTMOB_URL}10252.png",
    "Chelsea": f"{FOTMOB_URL}8455.png",
    "Crystal Palace": f"{FOTMOB_URL}9826.png",
    "Everton": f"{FOTMOB_URL}8668.png",
    "Leicester City": f"{FOTMOB_URL}8197.png",
    "Liverpool": f"{FOTMOB_URL}8650.png",
    "Manchester City": f"{FOTMOB_URL}8456.png",
    "Manchester United": f"{FOTMOB_URL}10260.png",
    "Newcastle United": f"{FOTMOB_URL}10261.png",
    "Norwich City": f"{FOTMOB_URL}9850.png",
    "Southampton": f"{FOTMOB_URL}8466.png",
    "Stoke City": f"{FOTMOB_URL}10194.png",
    "Sunderland": f"{FOTMOB_URL}8472.png",
    "Swansea City": f"{FOTMOB_URL}10003.png",
    "Tottenham Hotspur": f"{FOTMOB_URL}8586.png",
    "Watford": f"{FOTMOB_URL}9817.png",
    "West Bromwich Albion": f"{FOTMOB_URL}8659.png",
    "West Ham United": f"{FOTMOB_URL}8654.png",
}

teams = sorted(
    getCompetitionTeamNames(competitionId=COMPETITION_ID, seasonId=SEASON_ID)
)[:20]

fig = plt.figure(figsize=(10, 7), dpi=300)
ax = plt.subplot()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_axis_off()

teamPasses = {}

for idx, team in enumerate(tqdm(teams, leave=False)):
    games = getAllTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)

    teamPasses[team] = {
        "longAttempted": 0,
        "shortAttempted": 0,
        "longCompleted": 0,
        "shortCompleted": 0,
    }

    for gameId in tqdm(games, leave=False):
        match = fetchMatch(gameId, load_360=True)
        df = match.events

        PLAYER_NAME = findPlayerNameByRole(df, team, "Goalkeeper")
        isPass = df["type_name"] == "Pass"
        isTargetPlayer = df["player_name"] == PLAYER_NAME
        gkPasses = df[isTargetPlayer & isPass]

        for index, row in gkPasses.iterrows():
            passHeight = row["extra"]["pass"]["height"]["name"]
            passLength = row["extra"]["pass"]["length"]
            passExtra = row.get("extra", {}).get("pass", {})
            passSuccessful = "outcome" not in passExtra
            threshold = 25 if passHeight == "High Pass" else 45
            isLong = passLength > threshold
            keyAttempt = "longAttempted" if isLong else "shortAttempted"
            keyComplete = "longCompleted" if isLong else "shortCompleted"
            teamPasses[team][keyAttempt] += 1
            if passSuccessful:
                teamPasses[team][keyComplete] += 1


df = (
    pd.DataFrame.from_dict(teamPasses, orient="index")
    .reset_index()
    .rename(columns={"index": "team"})
)

df["shareOfLong"] = df["longAttempted"] / (df["longAttempted"] + df["shortAttempted"])
df["longCompletionRate"] = df["longCompleted"] / df["longAttempted"]


IMAGE_W, IMAGE_H = 0.025, 0.025

fig = plt.figure(
    figsize=(8, 8),
    dpi=100,
)
ax = plt.subplot()
ax.set_facecolor("#eeeeee")
ax.grid(visible=True, ls="--", color="lightgrey")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.set_ylabel("Long pass completion rate", labelpad=10)
ax.set_xlabel("Share of long passes", labelpad=10)
ax.set_xlim(np.min(df["shareOfLong"]) - IMAGE_W, np.max(df["shareOfLong"]) + IMAGE_W)
ax.set_ylim(
    np.min(df["longCompletionRate"]) - IMAGE_H,
    np.max(df["longCompletionRate"]) + IMAGE_H,
)

for _, row in df.iterrows():
    team = row["team"]
    x = row["shareOfLong"]
    y = row["longCompletionRate"]

    img = Image.open(urllib.request.urlopen(TEAM_LOGO_URL[team])).convert("LA")
    image_ax = ax.inset_axes(
        [x - IMAGE_W / 2, y - IMAGE_H / 2, IMAGE_W, IMAGE_H], transform=ax.transData
    )
    image_ax.imshow(img)
    image_ax.axis("off")


fig.patch.set_facecolor("#f9f7f3")

saveFigure(
    fig,
    f"{folder}/scatterplotShareOfLong.png",
)
