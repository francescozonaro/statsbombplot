"""Command-line arguments and interactive prompts shared by the example scripts.

A script declares the flags it needs (`game_args` / `season_args`) and resolves them
(`resolve_game` / `resolve_season`). Whatever was not passed on the command line is asked
for interactively, offering only choices that exist in the StatsBomb open data.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, Sequence, TypeVar

import pandas as pd

from .data import get_competitions, get_games

T = TypeVar("T")


def is_interactive() -> bool:
    """True when we can prompt the user (stdin is a terminal)."""
    return sys.stdin.isatty()


def _require_terminal(*flags: str) -> None:
    if not is_interactive():
        raise SystemExit(f"error: {' and '.join(flags)} required when not running in a terminal")


def choose(title: str, options: Sequence[tuple[T, str]]) -> T:
    """Show a numbered list and return the value of the option the user picks.

    Typing text (or a number outside the list, such as a year) filters the list; an empty
    answer clears the filter.
    """
    if not options:
        raise SystemExit(f"error: no choices available for: {title}")
    if len(options) == 1:
        print(f"{title} {options[0][1]} (only choice)")
        return options[0][0]

    shown = list(options)
    print(f"\n{title}")
    while True:
        for number, (_, label) in enumerate(shown, 1):
            print(f"  {number:>3}. {label}")
        try:
            answer = input("Pick a number, or type text to filter: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit("\naborted") from None

        if answer.isdigit() and 1 <= int(answer) <= len(shown):
            return shown[int(answer) - 1][0]
        elif not answer:
            shown = list(options)
        else:  # text, or a number out of range (e.g. a year): filter
            matches = [o for o in options if answer.lower() in o[1].lower()]
            if matches:
                shown = matches
            else:
                print(f'Nothing matches "{answer}".')


def _competition_label(row: Any) -> str:
    women = " [women]" if row.competition_gender == "female" else ""
    return f"{row.competition_name} ({row.country_name}){women}"


def _game_label(row: Any) -> str:
    in_league = row.competition_stage == "Regular Season" and pd.notna(row.game_day)
    when = f"GW {int(row.game_day)}" if in_league else row.competition_stage
    if pd.notna(row.home_score) and pd.notna(row.away_score):
        result = (
            f"{row.home_team_name} {int(row.home_score)}-{int(row.away_score)} {row.away_team_name}"
        )
    else:
        result = f"{row.home_team_name} vs {row.away_team_name}"
    return f"{row.game_date:%Y-%m-%d} · {when} · {result}"


def resolve_season(competition_id: int | None, season_id: int | None) -> tuple[int, int]:
    """Return (competition_id, season_id), prompting for whichever is missing."""
    if competition_id is None or season_id is None:
        _require_terminal(
            *(
                f
                for f, v in (("--competition-id", competition_id), ("--season-id", season_id))
                if v is None
            )
        )

    competitions = get_competitions()

    if competition_id is None:
        unique = competitions.drop_duplicates("competition_id").sort_values("competition_name")
        competition_id = choose(
            "Competition:",
            [(int(r.competition_id), _competition_label(r)) for r in unique.itertuples()],
        )

    seasons = competitions[competitions["competition_id"] == competition_id]
    if season_id is None:
        seasons = seasons.sort_values("season_name", ascending=False)
        season_id = choose(
            "Season:", [(int(r.season_id), r.season_name) for r in seasons.itertuples()]
        )

    if not ((seasons["season_id"] == season_id).any()):
        raise SystemExit(
            f"error: no open data for competition {competition_id}, season {season_id}"
        )
    return competition_id, season_id


def resolve_game(game_id: int | None) -> int:
    """Return a game id, walking the user through competition, season and game if missing."""
    if game_id is not None:
        return game_id
    _require_terminal("--game-id")
    competition_id, season_id = resolve_season(None, None)
    games = get_games(competition_id, season_id).sort_values("game_date")
    return choose("Game:", [(int(r.game_id), _game_label(r)) for r in games.itertuples()])


def game_args(description: str) -> argparse.Namespace:
    """Parse the flags of a single-game script."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--game-id", type=int, help="StatsBomb game id (asked if omitted)")
    return parser.parse_args()


def season_args(description: str) -> argparse.Namespace:
    """Parse the flags of a whole-season script."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--competition-id", type=int, help="StatsBomb competition id (asked if omitted)"
    )
    parser.add_argument("--season-id", type=int, help="StatsBomb season id (asked if omitted)")
    return parser.parse_args()
