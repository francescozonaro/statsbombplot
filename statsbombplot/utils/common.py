import warnings

from statsbombpy.api_client import NoAuthWarning
from .loader import Loader
from requests.exceptions import HTTPError
from models import Match

warnings.simplefilter("ignore", NoAuthWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


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
        print(f"Fetching events for gameId: {gameId}")
        matchEvents = api.events(gameId, load_360=load_360)
    except HTTPError:
        print(f"No 360 data available for gameId: {gameId}. Loading basic data.")
        matchEvents = api.events(gameId, load_360=False)

    print(f"Fetching players and teams for gameId: {gameId}")
    players = api.players(gameId)
    teams = api.teams(gameId)

    # Create and return the Match object
    match = Match(gameId, matchEvents, teams, players)
    print(f"Match object created for gameId: {gameId}")

    return match


def fetchAllSeasonMatches(competitionId, seasonId, load_360=True):
    pass


def addNotes(ax, author, extra_text=None):
    """
    Adds author tag and extra text to the bottom left of the plot.
    """
    ax.text(105.8, -2.1, author, fontsize=10, va="center")

    if extra_text:
        for i, text in enumerate(extra_text):
            ax.text(
                0,
                -2.1 - 2 * i,
                text,
                fontsize=7,
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
        frameon=True,
        handletextpad=0.5,
    )


def saveFigure(fig, filename, dpi=300):
    """
    Saves the figure to a file with the given dpi.
    """
    fig.savefig(filename, bbox_inches="tight", format="png", dpi=dpi)
