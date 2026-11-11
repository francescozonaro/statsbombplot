import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import ImageEnhance
from tqdm import tqdm

from statsbombplot.cli import resolve_season, season_args
from statsbombplot.config import FIG_BACKGROUND_COLOR, GRAY_HEX, OUTPUT_DIR
from statsbombplot.data import fetch_match, get_team_matches_from_season, get_teams_by_season
from statsbombplot.plotting import apply_style, load_team_logo, save_figure

LOGO_W = 0.025
LOGO_H = 0.025


def main():
    apply_style()
    args = season_args("Goalkeeper long-pass share vs. completion rate for every team in a season.")
    competition_id, season_id = resolve_season(args.competition_id, args.season_id)
    # Data
    teams = sorted(get_teams_by_season(competition_id, season_id))
    records = []
    for team in tqdm(teams, leave=False):
        games = get_team_matches_from_season(competition_id, season_id, team)
        long_attempted = short_attempted = long_completed = short_completed = 0

        for game_id in tqdm(games, leave=False):
            match = fetch_match(game_id, load_360=True)
            df = match.events

            gk_passes = df[
                (df["type_name"] == "Pass")
                & (df["team_name"] == team)
                & (df["position_name"] == "Goalkeeper")
            ]

            heights = gk_passes["extra"].apply(lambda x: x["pass"]["height"]["name"])
            lengths = gk_passes["extra"].apply(lambda x: x["pass"]["length"])
            successful = gk_passes["extra"].apply(lambda x: "outcome" not in x["pass"])

            thresholds = np.where(heights == "High Pass", 25, 45)
            is_long = lengths.values > thresholds

            long_attempted += is_long.sum()
            short_attempted += (~is_long).sum()
            long_completed += (is_long & successful.values).sum()
            short_completed += (~is_long & successful.values).sum()

        records.append(
            {
                "team": team,
                "long_att": long_attempted,
                "short_att": short_attempted,
                "long_cmp": long_completed,
                "short_cmp": short_completed,
            }
        )

    pdf = pd.DataFrame(records)
    pdf["share_of_long"] = pdf["long_att"] / (pdf["long_att"] + pdf["short_att"])
    pdf["pass_completion_rate"] = (pdf["long_cmp"]) / (pdf["long_att"])

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

    min_x, max_x = np.min(pdf["share_of_long"]), np.max(pdf["share_of_long"])
    min_y, max_y = np.min(pdf["pass_completion_rate"]), np.max(pdf["pass_completion_rate"])
    pad_x = (max_x - min_x) * 0.1
    pad_y = (max_y - min_y) * 0.1
    ax.set_xlim(min_x - pad_x, max_x + pad_x)
    ax.set_ylim(min_y - pad_y, max_y + pad_y)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))

    for _, row in pdf.iterrows():
        team = row["team"]
        x = row["share_of_long"]
        y = row["pass_completion_rate"]

        img = load_team_logo(team)
        if img is None:  # no logo for this team: label the point with its name
            ax.text(x, y, team, ha="center", va="center", fontsize=7, color=GRAY_HEX)
            continue
        img = ImageEnhance.Color(img).enhance(0.5)  # Lowers saturation
        img_x = x - LOGO_W / 2
        img_y = y - LOGO_H / 2
        image_ax = ax.inset_axes([img_x, img_y, LOGO_W, LOGO_H], transform=ax.transData)
        image_ax.imshow(img)
        image_ax.axis("off")

    # Median
    x0 = pdf["share_of_long"].median()
    y0 = pdf["pass_completion_rate"].median()
    ax.axvline(x0, ls="--", lw=1, color=GRAY_HEX)
    ax.axhline(y0, ls="--", lw=1, color=GRAY_HEX)

    fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)

    save_figure(
        fig,
        OUTPUT_DIR / "goalkeeper_pass_completion" / f"{competition_id}_{season_id}.png",
    )


if __name__ == "__main__":
    main()
