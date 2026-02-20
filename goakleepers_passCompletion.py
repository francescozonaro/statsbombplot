import matplotlib.pyplot as plt
import os
import numpy as np
import urllib.request
import pandas as pd

from PIL import Image, ImageEnhance
from tqdm import tqdm
from utils import (
    getTeamMatchesFromSeason,
    getTeamsBySeason,
    fetchMatch,
    saveFigure,
)


# Constants
folder = os.path.join("imgs/", str(f"goalkeeperPasses"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

COMPETITION_ID = 2
SEASON_ID = 27
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


def _findKeeper(df, team, role):
    startingXI = df[
        (df["type_name"] == "Starting XI") & (df["team_name"] == team)
    ].iloc[0]
    lineup = startingXI["extra"]["tactics"]["lineup"]
    candidate = next(player for player in lineup if player["position"]["name"] == role)
    return candidate["player"]["name"]


# Data preparation
teams = sorted(getTeamsBySeason(competitionId=COMPETITION_ID, seasonId=SEASON_ID))[:20]
teamPasses = {}

for idx, team in enumerate(tqdm(teams, leave=False)):
    games = getTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)

    teamPasses[team] = {
        "longAttempted": 0,
        "shortAttempted": 0,
        "longCompleted": 0,
        "shortCompleted": 0,
    }

    for gameId in tqdm(games, leave=False):
        match = fetchMatch(gameId, load_360=True)
        df = match.events

        KEEPER_NAME = _findKeeper(df, team, "Goalkeeper")
        isPass = df["type_name"] == "Pass"
        isKeeper = df["player_name"] == KEEPER_NAME
        gkPasses = df[isKeeper & isPass]

        for index, row in gkPasses.iterrows():
            passHeight = row["extra"]["pass"]["height"]["name"]
            passLength = row["extra"]["pass"]["length"]
            passSuccessful = "outcome" not in row["extra"]["pass"]

            longThreshold = 25 if passHeight == "High Pass" else 45
            isLong = passLength > longThreshold

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
# df["passCompletionRate"] = (df["longCompleted"] + df["shortCompleted"]) / (
#     df["longAttempted"] + df["shortAttempted"]
# )
df["passCompletionRate"] = (df["longCompleted"]) / (df["longAttempted"])

# Main figure
LOGO_W, LOGO_H = 0.025, 0.025
fig = plt.figure(
    figsize=(8, 8),
    dpi=100,
)
ax = plt.subplot()
ax.set_facecolor("#eeeeee")
ax.grid(visible=True, ls="--", color="lightgrey")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.set_xlabel("GK share of long passes", labelpad=10)
# ax.set_ylabel("GK pass completion rate", labelpad=10)
ax.set_ylabel("GK long passes completion rate", labelpad=10)

minX, maxX = np.min(df["shareOfLong"]), np.max(df["shareOfLong"])
minY, maxY = np.min(df["passCompletionRate"]), np.max(df["passCompletionRate"])
ax.set_xlim(minX - LOGO_W, maxX + LOGO_W)
ax.set_ylim(minY - 2 * LOGO_H, maxY + 2 * LOGO_H)

for _, row in df.iterrows():
    team = row["team"]
    x = row["shareOfLong"]
    y = row["passCompletionRate"]

    img = Image.open(urllib.request.urlopen(TEAM_LOGO_URL[team])).convert("RGBA")
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(0.5)  # Lowers saturation
    image_ax = ax.inset_axes(
        [x - LOGO_W / 2, y - LOGO_H / 2, LOGO_W, LOGO_H], transform=ax.transData
    )
    image_ax.imshow(img)
    image_ax.axis("off")

# Median
x0 = df["shareOfLong"].median()
y0 = df["passCompletionRate"].median()
ax.axvline(x0, ls="--", lw=1, color="grey")
ax.axhline(y0, ls="--", lw=1, color="grey")

# Curve
# x = df["shareOfLong"].to_numpy()
# y = df["passCompletionRate"].to_numpy()
# coeffs = np.polyfit(x, y, 2)
# p = np.poly1d(coeffs)
# x_line = np.linspace(x.min(), x.max(), 200)
# y_line = p(x_line)
# ax.plot(x_line, y_line, lw=2, ls="--", color="#d47e68")

# Annotations
tl_xy = (minX - LOGO_W, maxY + 2 * LOGO_H)
br_xy = (maxX + LOGO_W, minY - 2 * LOGO_H)
ax.annotate(
    "Rarely goes long,\nwith more precision",
    xy=tl_xy,
    xycoords="data",
    xytext=(5, -5),
    textcoords="offset points",
    ha="left",
    multialignment="center",
    va="top",
    fontsize=10,
)

ax.annotate(
    "Often goes long,\nwith less precision",
    xy=br_xy,
    xycoords="data",
    xytext=(-5, 5),
    textcoords="offset points",
    ha="right",
    multialignment="center",
    va="bottom",
    fontsize=10,
)

fig.patch.set_facecolor("#f9f7f3")

saveFigure(
    fig,
    f"{folder}/scatterplotShareOfLong.png",
)
