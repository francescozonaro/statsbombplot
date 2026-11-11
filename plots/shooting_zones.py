import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from tqdm import tqdm

from statsbombplot.cli import resolve_season, season_args
from statsbombplot.config import OUTPUT_DIR
from statsbombplot.data import fetch_match, get_team_matches_from_season, get_teams_by_season
from statsbombplot.pitch import HalfPitch
from statsbombplot.plotting import apply_style, make_matplotlib_grid, save_figure

VIZ_COLOR = "#a41212"
NORMALIZE_PER_TEAM = True


def main():
    apply_style()
    args = season_args("Shot density per team over a season.")
    competition_id, season_id = resolve_season(args.competition_id, args.season_id)
    teams = get_teams_by_season(competition_id=competition_id, season_id=season_id)
    teams = sorted(teams)

    pitch_width = 60
    pitch_height = 80
    pitch_ratio = pitch_height / pitch_width

    fig, axes = make_matplotlib_grid(len(teams), max_cols=5, subplot_width=4, ratio=pitch_ratio)

    max_shot_counts = 0
    shot_counts_map = {}

    for idx, team in enumerate(tqdm(teams, leave=False)):
        games = get_team_matches_from_season(competition_id, season_id, team)
        ZONES_X = 24
        ZONES_Y = 16
        RECT_X = 120 / ZONES_X
        RECT_Y = 80 / ZONES_Y
        shot_counts = np.zeros((ZONES_Y, ZONES_X))

        starting_points = []
        ending_points = []

        for game_id in tqdm(games, leave=False):
            match = fetch_match(game_id, load_360=True)
            df = match.events
            shots = df[df["type_name"] == "Shot"]

            for i, shot in shots.iterrows():
                start_x = shot["location"][0]
                start_y = shot["location"][1]
                zone_x = int(start_x // RECT_X)
                zone_y = int(start_y // RECT_Y)

                starting_points.append(shot["location"])
                ending_points.append(shot["extra"]["shot"]["end_location"])
                if zone_x < ZONES_X and zone_y < ZONES_Y:
                    shot_counts[zone_y, zone_x] += 1

        max_team_shots = np.max(shot_counts)
        max_shot_counts = max(max_shot_counts, max_team_shots)
        shot_counts_map[team] = shot_counts

    for idx, team in enumerate(teams):
        pitch = HalfPitch()
        pitch.draw(ax=axes[idx])

        shot_counts = shot_counts_map[team]

        if NORMALIZE_PER_TEAM:
            max_shot_counts = np.max(shot_counts)

        for i in range(ZONES_Y):
            for j in range(ZONES_X):
                count = shot_counts[i, j]
                alpha_factor = 0.8 * count / max_shot_counts
                fill_rect = Rectangle(
                    (j * RECT_X, 80 - (i + 1) * RECT_Y),
                    RECT_X,
                    RECT_Y,
                    facecolor=VIZ_COLOR,
                    alpha=alpha_factor,
                    edgecolor="none",
                    linewidth=0,
                    zorder=9,
                )
                # edge_rect = Rectangle(
                #     (j * RECT_X, 80 - (i + 1) * RECT_Y),
                #     RECT_X,
                #     RECT_Y,
                #     edgecolor="#555555",
                #     facecolor="none",
                #     linewidth=0.1,
                #     linestyle=(0, (3, 3)),
                #     zorder=9,
                # )

                axes[idx].add_patch(fill_rect)
                # axes[idx].add_patch(edge_rect)

        axes[idx].text(59.5, 87, team, fontsize=10, va="center")

    legend_elements = [
        plt.scatter(
            [],
            [],
            s=70,
            edgecolor="black",
            linewidth=0.6,
            facecolor="#ffffff",
            zorder=5,
            marker="s",
            label="Few shots",
        ),
        plt.scatter(
            [],
            [],
            s=70,
            edgecolor="black",
            linewidth=0.6,
            facecolor=VIZ_COLOR,
            zorder=5,
            marker="s",
            label="Many shots",
        ),
    ]

    fig.legend(
        handles=legend_elements,
        loc="upper center",
        ncol=len(legend_elements),
        bbox_to_anchor=(0.5, 0.93),
        fontsize=10,
        fancybox=True,
        frameon=False,
        handletextpad=0.5,
        handleheight=1.2,
    )

    save_figure(
        fig,
        OUTPUT_DIR / "shooting_zones" / f"{competition_id}_{season_id}.png",
    )


if __name__ == "__main__":
    main()
