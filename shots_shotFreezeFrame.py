import os

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt

from utils.commons import fetchMatch, saveFigure
from utils.config import FIG_BACKGROUND_COLOR
from utils.fullPitch import FullPitch

GAME_ID = 3795506  # EURO 2020 Final
HOME_TEAM_COLOR = "#3f8ae6"
AWAY_TEAM_COLOR = "#f04a5f"

folder = os.path.join("imgs/", str(GAME_ID))
os.makedirs(folder, exist_ok=True)
plt.rcParams["font.family"] = "Monospace"

### Data ###
match = fetchMatch(gameId=GAME_ID)
player_to_jersey_map = {
    player["player_name"]: player["jersey_number"]
    for _, player in match.players.iterrows()
}

df = match.events
is_shot = df["type_name"] == "Shot"
is_valid_period = df["period_id"] < 5
has_freeze = df["extra"].apply(
    lambda x: isinstance(x, dict)
    and "shot" in x
    and "freeze_frame" in x.get("shot", {})
)
validShots = df[is_shot & is_valid_period & has_freeze].reset_index(drop=True)

### Figures ###
for i, shot in validShots.iterrows():
    pitch = FullPitch()
    fig, ax = plt.subplots(1, 1, figsize=(15, 15 * (80 / 120)), dpi=300)
    pitch.draw(ax)
    fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)
    ax.set_facecolor(FIG_BACKGROUND_COLOR)

    x = shot.location[0]
    y = 80 - shot.location[1]
    shot_extra = shot["extra"]["shot"]
    shot_end_x = shot_extra["end_location"][0]
    shot_end_y = 80 - shot_extra["end_location"][1]
    shot_frame = shot_extra["freeze_frame"]
    shot_outcome = shot_extra["outcome"]["name"].lower()
    shot_technique = shot_extra["technique"]["name"].lower()
    shot_body_part = shot_extra["body_part"]["name"].lower()
    shot_xg = shot_extra["statsbomb_xg"]

    is_home = shot.team_id == match.homeTeamId
    home_color = HOME_TEAM_COLOR if is_home else AWAY_TEAM_COLOR
    away_color = AWAY_TEAM_COLOR if is_home else HOME_TEAM_COLOR

    ax.scatter(
        x,
        y,
        s=120,
        edgecolor="black",
        linewidth=0.6,
        facecolor=home_color,
        zorder=11,
        marker="*",
    )

    ax.plot(
        [x, shot_end_x],
        [y, shot_end_y],
        color=(0, 0, 0, 0.2),
        linewidth=0.9,
        zorder=5,
        linestyle="--",
    )

    for player in shot_frame:

        freezed_player_x = player["location"][0]
        freezed_player_y = 80 - player["location"][1]
        freezed_player_color = home_color if player["teammate"] else away_color

        ax.scatter(
            freezed_player_x,
            freezed_player_y,
            s=120,
            edgecolor="black",
            linewidth=0.6,
            facecolor=freezed_player_color,
            zorder=9,
            marker="o",
        )

        ax.text(
            freezed_player_x + 0.025,
            freezed_player_y - 0.05,
            str(player_to_jersey_map.get(player["player"]["name"], "?")),
            fontsize=6,
            zorder=9,
            ha="center",
            va="center",
            color="white",
            path_effects=[pe.withStroke(linewidth=1.5, foreground="black")],
        )

    legend_elements = [
        plt.scatter(
            [],
            [],
            s=90,
            edgecolor="black",
            linewidth=0.6,
            facecolor=home_color,
            zorder=5,
            marker="*",
            label="Shot location",
        ),
        plt.scatter(
            [],
            [],
            s=60,
            edgecolor="black",
            linewidth=0.6,
            facecolor=home_color,
            zorder=5,
            marker="o",
            label="Teammate",
        ),
        plt.scatter(
            [],
            [],
            s=60,
            edgecolor="black",
            linewidth=0.6,
            facecolor=away_color,
            zorder=5,
            marker="o",
            label="Opponent",
        ),
    ]

    formatted_time = f"{shot.minute}:{shot.second:02d}"
    extra = [
        f"At {formatted_time}, {shot.player_name} took a shot with an xG of {round(shot_xg, 3)}, which resulted in {shot_outcome}."
    ]

    pitch.addPitchLegend(ax, legend_elements)
    pitch.addPitchNotes(ax, extra_text=extra)
    saveFigure(fig, f"{folder}/shotFreezed_{i}.png")

    plt.close()
    # break  # remove to process all shots
