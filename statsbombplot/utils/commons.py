import warnings
import random
import unicodedata

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


def getAllTeamMatchesFromSeason(competitionId, seasonId, teamName):
    games = getStatsbombAPI().games(competition_id=competitionId, season_id=seasonId)
    games = games[
        games[["home_team_name", "away_team_name"]].isin([teamName]).any(axis=1)
    ]
    return list(games["game_id"])


def addNotes(ax, author, extra_text=None):
    """
    Adds author tag and extra text to the bottom left of the plot.
    """
    ax.text(104.8, -2.1, author, fontsize=10, va="center")

    if extra_text:
        for i, text in enumerate(extra_text):
            ax.text(
                0,
                -2.1 - 2 * i,
                text,
                fontsize=8,
                va="center",
                ha="left",
            )


def addLegend(ax, legendElements):
    """
    Adds legend at the top of the plot
    """
    ax.legend(
        handles=legendElements,
        loc="upper center",
        ncol=len(legendElements),
        bbox_to_anchor=(0.5, 1),
        fontsize=10,
        fancybox=True,
        frameon=False,
        handletextpad=0.5,
        handleheight=1.2,
    )


def saveFigure(fig, filename, dpi=300):
    """
    Saves the figure to a file with the given dpi.
    """
    fig.savefig(filename, bbox_inches="tight", format="png", dpi=dpi)


def normalizeString(input):
    return (
        unicodedata.normalize("NFKD", input).encode("ASCII", "ignore").decode("ASCII")
    )
