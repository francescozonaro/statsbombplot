import urllib.request

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from PIL import Image
from tqdm import tqdm

from statsbombplot.cli import resolve_season, season_args
from statsbombplot.config import (
    FIG_BACKGROUND_COLOR,
    GRAY_HEX,
    OUTPUT_DIR,
    PITCH_HEIGHT,
    PITCH_RATIO,
    PITCH_WIDTH,
    PLAIN_BLACK_HEX,
    PLAIN_WHITE_HEX,
    PURPLE_HEX,
    TEAM_LOGO_URL,
)
from statsbombplot.data import fetch_match, get_team_matches_from_season, get_teams_by_season
from statsbombplot.pitch import FullPitch, count_in_pitch_zones
from statsbombplot.plotting import apply_style, make_matplotlib_grid, save_figure

ZONES_X = 6
ZONES_Y = 5
ZONE_WIDTH = PITCH_WIDTH / ZONES_X
ZONE_HEIGHT = PITCH_HEIGHT / ZONES_Y

# Data


def main():
    apply_style()
    args = season_args("Where each team's goalkeeper distributes the ball over a season.")
    competition_id, season_id = resolve_season(args.competition_id, args.season_id)
    teams = sorted(get_teams_by_season(competition_id, season_id))
    pass_counts_map = {}

    for idx, team in enumerate(tqdm(teams, leave=False)):
        games = get_team_matches_from_season(competition_id, season_id, team)
        pass_counts = np.zeros((ZONES_Y, ZONES_X))

        for game_id in tqdm(games, leave=False):
            match = fetch_match(game_id, load_360=True)
            df = match.events

            is_pass = df["type_name"] == "Pass"
            is_team = df["team_name"] == team
            is_gk = df["position_name"] == "Goalkeeper"
            gk_passes = df[is_team & is_gk & is_pass]
            # Considering Statsbomb data, a pass is successful if there is no "outcome" in the extra dict. Any outcome specification is negative (eg. Incomplete, Out, Unknown)
            gk_passes = gk_passes[gk_passes["extra"].apply(lambda x: "outcome" not in x["pass"])]

            # Vectorized extraction of end locations and zone assignment
            end_locations = gk_passes["extra"].apply(lambda x: x["pass"]["end_location"])
            end_x = np.array([loc[0] for loc in end_locations])
            end_y = 80 - np.array([loc[1] for loc in end_locations])
            pass_counts += count_in_pitch_zones(
                end_x, end_y, ZONES_X, ZONES_Y, PITCH_WIDTH, PITCH_HEIGHT
            )

        pass_counts_map[team] = pass_counts

    # Figure
    fig, axes = make_matplotlib_grid(len(teams), max_cols=5, subplot_width=4, ratio=PITCH_RATIO)
    for idx, team in enumerate(teams):
        pitch = FullPitch()
        pitch.draw(ax=axes[idx])
        pass_counts = pass_counts_map[team]
        team_max_pass_count = np.max(pass_counts)
        share_of_team_passes = pass_counts / pass_counts.sum()
        non_zero_shares = share_of_team_passes[share_of_team_passes > 0]
        label_threshold = np.percentile(non_zero_shares, 95)
        for i in range(ZONES_Y):
            for j in range(ZONES_X):
                count = pass_counts[i, j]
                alpha_factor = 1 * count / team_max_pass_count
                fill_rect = Rectangle(
                    (j * ZONE_WIDTH, 80 - (i + 1) * ZONE_HEIGHT),
                    ZONE_WIDTH,
                    ZONE_HEIGHT,
                    facecolor=PURPLE_HEX,
                    edgecolor=GRAY_HEX,
                    alpha=alpha_factor,
                    linewidth=0.2,
                    zorder=9,
                )
                axes[idx].add_patch(fill_rect)

                cur_zone_passes = share_of_team_passes[i, j]
                if cur_zone_passes >= label_threshold:
                    axes[idx].text(
                        j * ZONE_WIDTH + ZONE_WIDTH / 2,
                        80 - (i + 1) * ZONE_HEIGHT + ZONE_HEIGHT / 2,
                        f"{cur_zone_passes * 100:.1f}%",
                        ha="center",
                        va="center",
                        fontsize=7,
                        color="#ffffff",
                        zorder=10,
                        path_effects=[pe.withStroke(linewidth=0.5, foreground="black")],
                    )

        img = Image.open(urllib.request.urlopen(TEAM_LOGO_URL[team])).convert("LA")
        image_ax = axes[idx].inset_axes([0.02, 0.98, 0.10, 0.10], transform=axes[idx].transAxes)
        image_ax.imshow(img)
        image_ax.axis("off")

        axes[idx].text(13, 87, team, fontsize=10, va="center")

    legend_elements = [
        plt.scatter(
            [],
            [],
            s=70,
            edgecolor=PLAIN_BLACK_HEX,
            linewidth=0.6,
            facecolor=PLAIN_WHITE_HEX,
            zorder=5,
            marker="s",
            label="Few GK distributions",
        ),
        plt.scatter(
            [],
            [],
            s=70,
            edgecolor=PLAIN_BLACK_HEX,
            linewidth=0.6,
            facecolor=PURPLE_HEX,
            zorder=5,
            marker="s",
            label="Many GK distributions",
        ),
    ]

    fig.legend(
        handles=legend_elements,
        loc="upper center",
        ncol=len(legend_elements),
        bbox_to_anchor=(0.5, 0.95),
        fontsize=10,
        fancybox=True,
        frameon=False,
        handletextpad=0.5,
        handleheight=1,
    )

    fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)

    save_figure(
        fig,
        OUTPUT_DIR / "goalkeeper_zonal_pass_distribution" / f"{competition_id}_{season_id}.png",
    )


if __name__ == "__main__":
    main()
