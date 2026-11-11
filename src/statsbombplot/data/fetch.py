from __future__ import annotations

import hashlib
import pickle
import random
import warnings
from pathlib import Path

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


def get_random_match_id(seed: int | None = None) -> int:
    """Pick a random game from a random competition/season (reproducible with `seed`)."""
    if seed is not None:
        random.seed(seed)

    api = get_statsbomb_api()
    competitions = api.competitions()
    random_row = competitions.sample(n=1, random_state=random.randint(0, 10000)).iloc[0]
    games = api.games(random_row.competition_id, random_row.season_id)
    random_game = games.sample(n=1, random_state=random.randint(0, 10000)).iloc[0]
    return random_game.game_id


def get_random_competition_and_season_ids(seed: int | None = None) -> tuple[int, int]:
    """Pick a random (competition_id, season_id) pair (reproducible with `seed`)."""
    if seed is not None:
        random.seed(seed)

    api = get_statsbomb_api()
    competitions = api.competitions()
    random_row = competitions.sample(n=1, random_state=random.randint(0, 10000)).iloc[0]
    return random_row.competition_id, random_row.season_id


def get_all_matches_from_season(competition_id: int, season_id: int) -> list[int]:
    """Return the ids of all games in a competition season."""
    games = get_statsbomb_api().games(competition_id=competition_id, season_id=season_id)
    return list(games["game_id"])


def get_teams_by_season(competition_id: int, season_id: int) -> list[str]:
    """Return the names of the teams that played in a competition season."""
    games = get_statsbomb_api().games(competition_id=competition_id, season_id=season_id)
    return list(games["home_team_name"].unique())


def get_team_matches_from_season(competition_id: int, season_id: int, team_name: str) -> list[int]:
    """Return the ids of all games a team played in a competition season."""
    games = get_statsbomb_api().games(competition_id=competition_id, season_id=season_id)
    games = games[games[["home_team_name", "away_team_name"]].isin([team_name]).any(axis=1)]
    return list(games["game_id"])
