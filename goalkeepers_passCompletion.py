import matplotlib.pyplot as plt
import os
import numpy as np
import urllib.request
import pandas as pd

from PIL import Image, ImageEnhance
from tqdm import tqdm
from utils.commons import (
    getTeamMatchesFromSeason,
    getTeamsBySeason,
    fetchMatch,
    saveFigure,
)
from utils.config import *

folder = os.path.join("imgs/", str(f"goalkeepers/passCompletion"))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

COMPETITION_ID = 2
SEASON_ID = 27
LOGO_W = 0.025
LOGO_H = 0.025

# Data
teams = sorted(getTeamsBySeason(COMPETITION_ID, SEASON_ID))
records = []
for team in tqdm(teams, leave=False):
    games = getTeamMatchesFromSeason(COMPETITION_ID, SEASON_ID, team)
    long_attempted = short_attempted = long_completed = short_completed = 0

    for gameId in tqdm(games, leave=False):
        match = fetchMatch(gameId, load_360=True)
        df = match.events

        gkPasses = df[
            (df["type_name"] == "Pass")
            & (df["team_name"] == team)
            & (df["position_name"] == "Goalkeeper")
        ]

        heights = gkPasses["extra"].apply(lambda x: x["pass"]["height"]["name"])
        lengths = gkPasses["extra"].apply(lambda x: x["pass"]["length"])
        successful = gkPasses["extra"].apply(lambda x: "outcome" not in x["pass"])

        thresholds = np.where(heights == "High Pass", 25, 45)
        is_long = lengths.values > thresholds

        long_attempted += is_long.sum()
        short_attempted += (~is_long).sum()
        long_completed += (is_long & successful.values).sum()
        short_completed += (~is_long & successful.values).sum()

    records.append(
        {
            "team": team,
            "longAtt": long_attempted,
            "shortAtt": short_attempted,
            "longCmp": long_completed,
            "shortCmp": short_completed,
        }
    )

pdf = pd.DataFrame(records)
pdf["shareOfLong"] = pdf["longAtt"] / (pdf["longAtt"] + pdf["shortAtt"])
pdf["passCompletionRate"] = (pdf["longCmp"]) / (pdf["longAtt"])

# Figure
fig = plt.figure(
    figsize=(8, 8),
    dpi=100,
)
ax = plt.subplot()
ax.set_facecolor(FIG_BACKGROUND_COLOR)
ax.grid(visible=True, ls="--", color="lightgray")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.set_xlabel("GK share of long passes", labelpad=10)
ax.set_ylabel("GK long passes completion rate", labelpad=10)

minX, maxX = np.min(pdf["shareOfLong"]), np.max(pdf["shareOfLong"])
minY, maxY = np.min(pdf["passCompletionRate"]), np.max(pdf["passCompletionRate"])
padX = (maxX - minX) * 0.1
padY = (maxY - minY) * 0.1
ax.set_xlim(minX - padX, maxX + padX)
ax.set_ylim(minY - padY, maxY + padY)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))

for _, row in pdf.iterrows():
    team = row["team"]
    x = row["shareOfLong"]
    y = row["passCompletionRate"]

    img = Image.open(urllib.request.urlopen(TEAM_LOGO_URL[team])).convert("RGBA")
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(0.5)  # Lowers saturation
    img_x = x - LOGO_W / 2
    img_y = y - LOGO_H / 2
    image_ax = ax.inset_axes([img_x, img_y, LOGO_W, LOGO_H], transform=ax.transData)
    image_ax.imshow(img)
    image_ax.axis("off")

# Median
x0 = pdf["shareOfLong"].median()
y0 = pdf["passCompletionRate"].median()
ax.axvline(x0, ls="--", lw=1, color=GRAY_HEX)
ax.axhline(y0, ls="--", lw=1, color=GRAY_HEX)

fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)

saveFigure(
    fig,
    f"{folder}/scatterplotShareOfLong.png",
)
