import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

from statsbombplot.config import FIG_BACKGROUND_COLOR, OUTPUT_DIR
from statsbombplot.data import fetch_match
from statsbombplot.pitch import FullPitch
from statsbombplot.plotting import apply_style, save_figure

GAME_ID = 3795506  # EURO 2020 Final
HOME_TEAM_COLOR = "#3f8ae6"
AWAY_TEAM_COLOR = "#f04a5f"
MARKER_SIZE = 120
LINE_WIDTH = 0.7
OUTCOME_STYLE = {
    "Goal": ("*", MARKER_SIZE * 1.5, 7),
    "Saved": ("o", MARKER_SIZE, 6),
}


def main():
    apply_style()
    ### Data ###
    match = fetch_match(game_id=GAME_ID)
    df = match.events
    is_shot = df["type_name"] == "Shot"
    is_valid_period = df["period_id"] < 5
    sdf = df[is_shot & is_valid_period].copy()
    is_home = sdf["team_id"] == match.home_team_id
    sdf.loc[~is_home, "plot_x"] = sdf.loc[~is_home, "location"].map(lambda loc: loc[0])
    sdf.loc[~is_home, "plot_y"] = sdf.loc[~is_home, "location"].map(lambda loc: 80 - loc[1])
    sdf.loc[is_home, "plot_x"] = sdf.loc[is_home, "location"].map(lambda loc: 120 - loc[0])
    sdf.loc[is_home, "plot_y"] = sdf.loc[is_home, "location"].map(lambda loc: loc[1])
    sdf["team_color"] = np.where(is_home, HOME_TEAM_COLOR, AWAY_TEAM_COLOR)

    ### Figure ###
    pitch = FullPitch()
    fig, ax = plt.subplots(1, 1, figsize=(15, 15 * (80 / 120)), dpi=300)
    fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)
    ax.set_facecolor(FIG_BACKGROUND_COLOR)
    pitch.draw(ax)

    for _, shot in sdf.iterrows():
        shot_extra = shot.extra["shot"]
        shot_xg = round(shot_extra["statsbomb_xg"], 3)
        scaled_xg = np.clip(shot_xg / 0.25, 0.1, 1.0)
        outcome = shot_extra["outcome"]["name"]
        shot_color = mcolors.to_rgba(shot.team_color, scaled_xg)

        marker, size, zorder = OUTCOME_STYLE.get(outcome, ("X", MARKER_SIZE, 5))
        ax.scatter(
            shot.plot_x,
            shot.plot_y,
            s=size,
            edgecolor="black",
            linewidth=LINE_WIDTH,
            facecolor=shot_color,
            zorder=zorder,
            marker=marker,
        )

    legend_markers = [
        ("X", "Off Target"),
        ("o", "On Target"),
        ("*", "Goal"),
    ]
    legend_elements = [
        plt.scatter(
            [],
            [],
            s=90,
            marker=marker,
            label=label,
            edgecolor="black",
            linewidth=0.6,
            facecolor=HOME_TEAM_COLOR,
            zorder=5,
        )
        for marker, label in legend_markers
    ]

    extra = [f"{match.home_team_name} vs {match.away_team_name}"]
    pitch.add_pitch_legend(ax, legend_elements)
    pitch.add_pitch_notes(ax, extra_text=extra)
    save_figure(fig, OUTPUT_DIR / "shot_map" / f"{match.game_id}.png")


if __name__ == "__main__":
    main()
