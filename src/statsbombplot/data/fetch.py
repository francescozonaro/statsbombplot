from __future__ import annotations

import hashlib
import pickle
import warnings
from functools import lru_cache
from pathlib import Path

import pandas as pd
from requests.exceptions import HTTPError
from statsbombpy.api_client import NoAuthWarning

from ..config import CACHE_DIR
from .loader import Loader
from .match import Match

warnings.simplefilter("ignore", NoAuthWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


def get_statsbomb_api() -> Loader:
    """Return a loader for the free StatsBomb open data (no credentials)."""
    api = Loader(creds={"user": "", "passwd": ""})
    return api


def _get_cache_path(game_id: int) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = f"match_{game_id}"
    filename = hashlib.md5(key.encode()).hexdigest() + ".pkl"
    return CACHE_DIR / filename


def fetch_match(game_id: int, load_360: bool = True) -> Match:
    """
    Fetch events, players and teams for a game and return a `Match`.

    Results are pickled in `CACHE_DIR`, so each game is downloaded only once.

    Parameters:
    - game_id: The ID of the game to fetch data for.
    - load_360: Whether to load 360-degree data (default: True). Falls back to
      events only if 360 data is not available for the game.
    """

    cache_path = _get_cache_path(game_id)

    if cache_path.exists():
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    api = get_statsbomb_api()
    # Fetch match events, players, and teams
    try:
        match_events = api.events(game_id, load_360=load_360)
    except HTTPError:
        match_events = api.events(game_id, load_360=False)

    players = api.players(game_id)
    teams = api.teams(game_id)

    # Create and return the Match object
    match = Match(game_id, match_events, teams, players)

    with open(cache_path, "wb") as f:
        pickle.dump(match, f)

    return match


@lru_cache(maxsize=None)
def get_competitions() -> pd.DataFrame:
    """Return every competition/season available in the StatsBomb open data."""
    return get_statsbomb_api().competitions()


@lru_cache(maxsize=None)
def get_games(competition_id: int, season_id: int) -> pd.DataFrame:
    """Return the games (date, gameweek, teams, score...) of a competition season."""
    return get_statsbomb_api().games(competition_id=competition_id, season_id=season_id)


def get_all_matches_from_season(competition_id: int, season_id: int) -> list[int]:
    """Return the ids of all games in a competition season."""
    return list(get_games(competition_id, season_id)["game_id"])


def get_teams_by_season(competition_id: int, season_id: int) -> list[str]:
    """Return the names of the teams that played in a competition season."""
    return list(get_games(competition_id, season_id)["home_team_name"].unique())


def get_team_matches_from_season(competition_id: int, season_id: int, team_name: str) -> list[int]:
    """Return the ids of all games a team played in a competition season."""
    games = get_games(competition_id, season_id)
    games = games[games[["home_team_name", "away_team_name"]].isin([team_name]).any(axis=1)]
    return list(games["game_id"])
