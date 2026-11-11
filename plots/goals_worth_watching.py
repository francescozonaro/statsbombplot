from datetime import datetime

import matplotlib.pyplot as plt
from tqdm import tqdm

from statsbombplot.cli import resolve_season, season_args
from statsbombplot.config import OUTPUT_DIR, PERSONAL_WATERMARK
from statsbombplot.data import fetch_match, get_all_matches_from_season, prefetch_matches
from statsbombplot.plotting import apply_style


class Banger:
    def __init__(
        self,
        player_name,
        team_name,
        opponent_name,
        minute,
        xg,
        location,
        end_location,
        technique,
        body_part,
        play_type,
    ):

        self.player_name = player_name
        player_parts = player_name.split()
        if len(player_parts) > 2:
            self.player_name = f"{player_parts[0]} {player_parts[-1]}"

        self.team_name = team_name
        self.opponent_name = opponent_name

        self.xg = xg
        self.location = location
        self.end_location = end_location
        self.technique = technique
        self.body_part = body_part
        self.play_type = play_type
        self.minute = minute

        x_banger = 1 - self.xg

        if self.technique != "Normal":
            x_banger += 0.1

        distance = ((40 - end_location[1]) ** 2 + (0 - end_location[2] * 2) ** 2) ** 0.5

        if distance > 5:
            x_banger += 0.1

        self.x_banger = round(x_banger, 2)


def main():
    apply_style()
    args = season_args("The most spectacular goals of a season, ranked by an xBanger score.")
    competition_id, season_id = resolve_season(args.competition_id, args.season_id)
    games = get_all_matches_from_season(competition_id=competition_id, season_id=season_id)
    prefetch_matches(games)
    bangers = []

    for game_id in tqdm(games, leave=False):
        match = fetch_match(game_id)
        events = match.events
        shots = events[events["type_name"] == "Shot"]
        for i, row in shots.iterrows():
            if row["extra"]["shot"]["outcome"]["name"] == "Goal":
                team_name = row["team_name"]
                if team_name == match.home_team_name:
                    opponent_name = match.away_team_name
                else:
                    opponent_name = match.home_team_name
                goal_minute = f"{row['minute']}:{row['second']:02d}"
                banger = Banger(
                    player_name=row["player_name"],
                    team_name=team_name,
                    opponent_name=opponent_name,
                    minute=goal_minute,
                    xg=round(row["extra"]["shot"]["statsbomb_xg"], 3),
                    location=row["location"],
                    end_location=row["extra"]["shot"]["end_location"],
                    technique=row["extra"]["shot"]["technique"]["name"],
                    body_part=row["extra"]["shot"]["body_part"]["name"],
                    play_type=row["extra"]["shot"]["type"]["name"],
                )
                bangers.append(banger)

    sorted_bangers = sorted(bangers, key=lambda b: b.x_banger, reverse=True)
    bangers_list = sorted_bangers[0:8]

    plt.figure(figsize=(10, 7), dpi=300)
    ax = plt.subplot()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

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
        s="Technique",
        size=9,
        ha="center",
        va="center",
        weight="extra bold",
    )
    ax.text(
        x=0.9,
        y=0.95,
        s="Play type",
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

    match_labels = []
    for i, banger in enumerate(bangers_list):
        row_height = 1 - 0.15 - i * 0.1

        if i % 2 == 0:
            ax.fill_between(
                x=[0.05, 0.95],
                y1=row_height - 0.05,
                y2=row_height + 0.05,
                color="#eceae5",
                zorder=-1,
            )

        ax.text(
            x=0.06,
            y=row_height,
            s=f"{banger.player_name}",
            weight="bold",
            size=9,
            ha="left",
            va="center",
        )
        match_label = ax.text(
            x=0.3,
            y=row_height,
            s=f"{banger.team_name} vs {banger.opponent_name} ({banger.minute})",
            weight="bold",
            size=9,
            ha="left",
            va="center",
        )
        match_labels.append(match_label)
        ax.text(
            x=0.66,
            y=row_height,
            s=f"{banger.x_banger}",
            size=9,
            ha="center",
            va="center",
        )
        ax.text(
            x=0.78,
            y=row_height,
            s=f"{banger.technique}",
            size=9,
            ha="center",
            va="center",
        )
        ax.text(
            x=0.9,
            y=row_height,
            s=f"{banger.play_type}",
            size=9,
            ha="center",
            va="center",
        )

    # Long team names: shrink only the rows whose match text would run into the xBanger column
    plt.gcf().canvas.draw()
    to_axes = ax.transAxes.inverted()
    available = 0.6 - 0.3
    for label in match_labels:
        width = to_axes.transform(label.get_window_extent())[1][0] - 0.3
        if width > available:
            label.set_fontsize(label.get_fontsize() * available / width)

    ax.text(
        x=0.05,
        y=0.04,
        s=f"Data from StatsBomb as of {datetime.now().strftime('%d %B %Y')}",
        size=7,
        ha="left",
        va="center",
    )
    ax.text(
        x=0.95,
        y=0.04,
        s=PERSONAL_WATERMARK,
        size=7,
        ha="right",
        va="center",
    )

    out = OUTPUT_DIR / "goals_worth_watching" / f"{competition_id}_{season_id}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(
        out,
        dpi=300,
        facecolor="#f9f7f3",
        bbox_inches="tight",
        edgecolor="none",
        transparent=False,
    )


if __name__ == "__main__":
    main()
