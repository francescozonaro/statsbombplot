from utils import getStatsbombAPI
from match import Match


def main():

    DEFAULT_GAME_ID = 3795506
    STATSBOMB_API = getStatsbombAPI()

    gameId = DEFAULT_GAME_ID
    matchEvents = STATSBOMB_API.events(gameId, load_360=True)
    matchPlayers = STATSBOMB_API.players(gameId)
    matchTeams = STATSBOMB_API.teams(gameId)

    match = Match(gameId, matchEvents, matchTeams, matchPlayers)
    match.drawPassingNetworks()


if __name__ == "__main__":
    main()
