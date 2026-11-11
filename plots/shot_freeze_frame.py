import matplotlib.patheffects as pe
import matplotlib.pyplot as plt

from statsbombplot.cli import game_args, resolve_game
from statsbombplot.config import (
    AWAY_TEAM_COLOR,
    FIG_BACKGROUND_COLOR,
    HOME_TEAM_COLOR,
    OUTPUT_DIR,
)
from statsbombplot.data import fetch_match
from statsbombplot.pitch import FullPitch
from statsbombplot.plotting import apply_style, save_figure

# StatsBomb outcome name -> phrase completing "...and it ___."
OUTCOME_PHRASE = {
    "Goal": "was a goal",
    "Saved": "was saved",
    "Saved Off Target": "was saved, but was off target anyway",
    "Saved to Post": "was saved onto the post",
    "Post": "hit the post",
    "Blocked": "was blocked",
    "Off T": "went off target",
    "Wayward": "went wayward",
}


def main():
    apply_style()
    args = game_args("Freeze frame of the players at the moment of a shot.")
    game_id = resolve_game(args.game_id)
    match = fetch_match(game_id=game_id)

    player_name_to_jersey_number = {
        player["player_name"]: player["jersey_number"] for _, player in match.players.iterrows()
    }

    df = match.events
    is_shot = df["type_name"] == "Shot"
    is_valid_period = df["period_id"] < 5
    has_freeze_frame = df["extra"].apply(
        lambda x: isinstance(x, dict) and "shot" in x and "freeze_frame" in x.get("shot", {})
    )

    valid_shots = df[is_shot & is_valid_period & has_freeze_frame].reset_index(drop=True)

    for i, shot in valid_shots.iterrows():
        is_home = shot.team_id == match.home_team_id
        pitch = FullPitch()

        fig, ax = plt.subplots(1, 1, figsize=(15, 15 * (80 / 120)), dpi=300)
        pitch.draw(ax)
        fig.patch.set_facecolor(FIG_BACKGROUND_COLOR)
        ax.set_facecolor(FIG_BACKGROUND_COLOR)

        x = shot.location[0]
        y = 80 - shot.location[1]
        end_x = shot["extra"]["shot"]["end_location"][0]
        end_y = 80 - shot["extra"]["shot"]["end_location"][1]
        frame = shot["extra"]["shot"]["freeze_frame"]

        if is_home:
            main_color = HOME_TEAM_COLOR
            opp_color = AWAY_TEAM_COLOR
        else:
            main_color = AWAY_TEAM_COLOR
            opp_color = HOME_TEAM_COLOR

        ax.scatter(
            x,
            y,
            s=120,
            edgecolor="black",
            linewidth=0.6,
            facecolor=main_color,
            zorder=11,
            marker="*",
        )

        ax.plot(
            [x, end_x],
            [y, end_y],
            color=(0, 0, 0, 0.2),
            linewidth=0.9,
            zorder=5,
            linestyle="--",
        )

        for player in frame:
            freezed_player_x = player["location"][0]
            freezed_player_y = 80 - player["location"][1]

            if player["teammate"]:
                freezed_player_color = main_color
            else:
                freezed_player_color = opp_color

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
                str(player_name_to_jersey_number.get(player["player"]["name"], "?")),
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
                facecolor=main_color,
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
                facecolor=main_color,
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
                facecolor=opp_color,
                zorder=5,
                marker="o",
                label="Opponent",
            ),
        ]

        outcome = shot.extra["shot"]["outcome"]["name"]
        shot_outcome = OUTCOME_PHRASE.get(outcome, f"ended as {outcome.lower()}")
        shot_technique = (
            shot.extra["shot"]["body_part"]["name"].lower()
            if shot.extra["shot"]["technique"]["name"].lower() == "normal"
            else shot.extra["shot"]["technique"]["name"].lower()
        )
        shot_value = shot.extra["shot"]["statsbomb_xg"]

        formatted_time = f"{shot.minute}:{shot.second:02d}"
        extra = [
            f"At {formatted_time}, {shot.player_name} took a shot with {shot_technique}, had an xG of {round(shot_value, 3)}, and it {shot_outcome}."
        ]

        pitch.add_pitch_legend(ax, legend_elements)
        pitch.add_pitch_notes(ax, extra_text=extra)
        save_figure(fig, OUTPUT_DIR / "shot_freeze_frame" / str(match.game_id) / f"{i}.png")

        plt.close(fig)


if __name__ == "__main__":
    main()
