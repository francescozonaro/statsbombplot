import os

from utils import getStatsbombAPI
from requests.exceptions import HTTPError
from match import Match


class TeamSeason:
    def __init__(self, gameIds, competitionName, seasonName, teamName):
        self.gameIds = gameIds
        self.competitionName = competitionName
        self.seasonName = seasonName
        self.teamName = teamName

        self.folder = f"imgs/{self.competitionName}/{self.seasonName}/{self.teamName}"
        os.makedirs(self.folder, exist_ok=True)

    def drawTeamSeasonShotFrames(self):

        STATSBOMB_API = getStatsbombAPI()

        for gameId in self.gameIds:
            try:
                matchEvents = STATSBOMB_API.events(gameId, load_360=True)
            except HTTPError:
                print(f"No 360 data available for this match. Loading basic data.")
                matchEvents = STATSBOMB_API.events(gameId, load_360=False)

            players = STATSBOMB_API.players(gameId)
            teams = STATSBOMB_API.teams(gameId)
            match = Match(
                gameId, matchEvents, teams, players, f"{self.folder}/{gameId}"
            )
            match.drawShotFrames()
