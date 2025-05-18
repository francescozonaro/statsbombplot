import warnings
import random
import unicodedata
import os
import pickle
import hashlib

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


def fetchRandomMatch(seed=None):
    if seed is not None:
        random.seed(seed)

    api = getStatsbombAPI()
    competitions = api.competitions()
    randomRow = competitions.sample(n=1, random_state=random.randint(0, 10000)).iloc[0]
    games = api.games(randomRow.competition_id, randomRow.season_id)
    randomGame = games.sample(n=1, random_state=random.randint(0, 10000)).iloc[0]
    return fetchMatch(gameId=randomGame.game_id, load_360=True)


def getAllMatchesFromSeason(competitionId, seasonId):
    games = getStatsbombAPI().games(competition_id=competitionId, season_id=seasonId)
    return list(games["game_id"])


def getCompetitionTeamNames(competitionId, seasonId):
    games = getStatsbombAPI().games(competition_id=competitionId, season_id=seasonId)
    return list(games["home_team_name"].unique())


def getAllTeamMatchesFromSeason(competitionId, seasonId, teamName):
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
