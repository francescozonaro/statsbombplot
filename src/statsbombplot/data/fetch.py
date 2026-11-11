from __future__ import annotations

import hashlib
import multiprocessing
import os
import pickle
import tempfile
import warnings
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import pandas as pd
from requests.exceptions import HTTPError
from statsbombpy.api_client import NoAuthWarning
from tqdm import tqdm

from ..config import CACHE_DIR
from .loader import Loader
from .match import Match

warnings.simplefilter("ignore", NoAuthWarning)
# Only silence FutureWarnings raised inside statsbombpy, not the user's own code
warnings.filterwarnings("ignore", category=FutureWarning, module=r"statsbombpy")


def get_statsbomb_api() -> Loader:
    """Return a loader for the free StatsBomb open data (no credentials)."""
    api = Loader(creds={"user": "", "passwd": ""})
    return api


def _get_cache_path(game_id: int) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = f"match_{game_id}"
    filename = hashlib.md5(key.encode()).hexdigest() + ".pkl"
    return CACHE_DIR / filename


def fetch_match(game_id: int) -> Match:
    """
    Fetch events, players and teams for a game and return a `Match`.

    360 data is loaded when the game has it. Results are pickled in `CACHE_DIR`, so each
    game is downloaded only once; a cache file that cannot be read is downloaded again.
    """
    cache_path = _get_cache_path(game_id)

    if cache_path.exists():
        try:
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError, AttributeError, ImportError):
            pass  # truncated or outdated cache file: fall through and download again

    api = get_statsbomb_api()
    try:
        match_events = api.events(game_id, load_360=True)
    except HTTPError:  # no 360 data for this game
        match_events = api.events(game_id, load_360=False)

    match = Match(game_id, match_events, api.teams(game_id), api.players(game_id))

    # Write to a temp file first: an interrupted write must never leave a broken cache file
    fd, tmp_path = tempfile.mkstemp(dir=CACHE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            pickle.dump(match, f)
        os.replace(tmp_path, cache_path)
    except BaseException:
        Path(tmp_path).unlink(missing_ok=True)
        raise

    return match


def _warm(game_id: int) -> None:
    fetch_match(game_id)


def prefetch_matches(game_ids: Iterable[int], workers: int = 4) -> None:
    """Download and cache many games in parallel, so later `fetch_match` calls are instant.

    Uses processes, not threads: statsbombpy keeps an SQLite HTTP cache that is not safe to share
    between threads (it crashed the interpreter). Games that are already cached are skipped.
    """
    todo = [i for i in dict.fromkeys(game_ids) if not _get_cache_path(i).exists()]
    if workers <= 1 or len(todo) <= 1:
        for game_id in tqdm(todo, desc="Matches", leave=False):
            _warm(game_id)
        return
    # "spawn" so workers never inherit the parent's open SQLite connections
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as pool:
        list(tqdm(pool.map(_warm, todo), total=len(todo), desc="Matches", leave=False))


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
    games = get_games(competition_id, season_id)
    # home and away: in partial data (e.g. only one club's games) some teams never play at home
    return sorted(set(games["home_team_name"]) | set(games["away_team_name"]))


def get_team_matches_from_season(competition_id: int, season_id: int, team_name: str) -> list[int]:
    """Return the ids of all games a team played in a competition season."""
    games = get_games(competition_id, season_id)
    games = games[games[["home_team_name", "away_team_name"]].isin([team_name]).any(axis=1)]
    return list(games["game_id"])
