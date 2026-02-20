import math
import warnings
import random
import unicodedata
import os
import pickle
import hashlib
import numpy as np
import matplotlib.pyplot as plt
import urllib.request

from PIL import Image
from statsbombpy.api_client import NoAuthWarning
from .loader import Loader
from requests.exceptions import HTTPError
from models import Match

warnings.simplefilter("ignore", NoAuthWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# Fetching
def getStatsbombAPI():
    api = Loader(creds={"user": "", "passwd": ""})
    return api


def _get_cache_path(gameId):
    CACHE_DIR = "match_cache"
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = f"match_{gameId}"
    filename = hashlib.md5(key.encode()).hexdigest() + ".pkl"
    return os.path.join(CACHE_DIR, filename)


def fetchMatch(gameId, load_360=True):
    """
    Fetches events, players, and teams from the API and creates a Match object.

    Parameters:
    - gameId: The ID of the game to fetch data for.
    - api: The StatsBomb API instance.
    - folder: The base folder to store images or outputs.
    - load_360: Whether to load 360-degree data (default: True).

    Returns:
    - match: The Match object created using fetched data.
    - folder_path: The path where match-related images or outputs can be stored.
    """

    cache_path = _get_cache_path(gameId)

    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    api = getStatsbombAPI()
    # Fetch match events, players, and teams
    try:
        matchEvents = api.events(gameId, load_360=load_360)
    except HTTPError:
        matchEvents = api.events(gameId, load_360=False)

    players = api.players(gameId)
    teams = api.teams(gameId)

    # Create and return the Match object
    match = Match(gameId, matchEvents, teams, players)

    with open(cache_path, "wb") as f:
        pickle.dump(match, f)

    return match


def getRandomMatchId(seed=None):
    if seed is not None:
        random.seed(seed)

    api = getStatsbombAPI()
    competitions = api.competitions()
    randomRow = competitions.sample(n=1, random_state=random.randint(0, 10000)).iloc[0]
    games = api.games(randomRow.competition_id, randomRow.season_id)
    randomGame = games.sample(n=1, random_state=random.randint(0, 10000)).iloc[0]
    return randomGame.game_id


def getRandomCompetitionAndSeasonIds(seed=None):
    if seed is not None:
        random.seed(seed)

    api = getStatsbombAPI()
    competitions = api.competitions()
    randomRow = competitions.sample(n=1, random_state=random.randint(0, 10000)).iloc[0]
    return randomRow.competition_id, randomRow.season_id


def getAllMatchesFromSeason(competitionId, seasonId):
    games = getStatsbombAPI().games(competition_id=competitionId, season_id=seasonId)
    return list(games["game_id"])


def getTeamsBySeason(competitionId, seasonId):
    games = getStatsbombAPI().games(competition_id=competitionId, season_id=seasonId)
    return list(games["home_team_name"].unique())


def getTeamMatchesFromSeason(competitionId, seasonId, teamName):
    games = getStatsbombAPI().games(competition_id=competitionId, season_id=seasonId)
    games = games[
        games[["home_team_name", "away_team_name"]].isin([teamName]).any(axis=1)
    ]
    return list(games["game_id"])


def saveFigure(fig, filename, dpi=300):
    """
    Saves the figure to a file with the given dpi.
    """
    fig.savefig(filename, bbox_inches="tight", format="png", dpi=dpi)


def normalizeString(input):
    return (
        unicodedata.normalize("NFKD", input).encode("ASCII", "ignore").decode("ASCII")
    )


def count_in_pitch_zones(x, y, zones_x, zones_y, pitch_w=120, pitch_h=80):
    """
    Bin (x, y) coordinates into a grid and count occurrences per zone. Defaults to StatsBomb pitch dimensions (120x80) and orientation (y flipped).

    Parameters
    ----------
    x : np.ndarray
        Array of x coordinates.
    y : np.ndarray
        Array of y coordinates, already adjusted for orientation
        (e.g. 80 - raw_y for StatsBomb data).
    zones_x : int
        Number of horizontal zones to divide the pitch into.
    zones_y : int
        Number of vertical zones to divide the pitch into.
    pitch_w : float, optional
        Total pitch width in coordinate units. Default is 120 (StatsBomb).
    pitch_h : float, optional
        Total pitch height in coordinate units. Default is 80 (StatsBomb).

    Returns
    -------
    np.ndarray
        A (zones_y, zones_x) array where each cell contains the count of
        coordinates that fell within that zone. Coordinates outside the
        pitch boundaries are excluded.
    """
    rect_x, rect_y = pitch_w / zones_x, pitch_h / zones_y
    zx = (x // rect_x).astype(int)
    zy = (y // rect_y).astype(int)
    valid = (zx < zones_x) & (zy < zones_y)
    counts = np.zeros((zones_y, zones_x))
    np.add.at(counts, (zy[valid], zx[valid]), 1)
    return counts


def make_matplotlib_grid(n_items, max_cols=5, subplot_width=4, ratio=80 / 120):
    """
    Create a grid of matplotlib subplots, hiding any unused axes.

    Parameters
    ----------
    n_items : int
        Number of subplots that will actually be used.
    max_cols : int, optional
        Maximum number of columns. Default is 5.
    subplot_width : float, optional
        Width of each subplot in inches. Default is 4.
    ratio : float, optional
        Height-to-width ratio of each subplot. Default is 80/120
        (StatsBomb pitch proportions).

    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : np.ndarray
        Flattened array of Axes. First n_items are active,
        the rest are hidden.
    """
    n_cols = min(n_items, max_cols)
    n_rows = math.ceil(n_items / n_cols)
    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(subplot_width * n_cols, subplot_width * n_rows * ratio)
    )
    axes = np.atleast_1d(axes).flatten()
    for i in range(n_items, len(axes)):
        axes[i].axis("off")
    return fig, axes
