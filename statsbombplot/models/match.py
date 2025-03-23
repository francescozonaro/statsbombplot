class Match:
    def __init__(self, gameId, matchEvents, matchTeams, matchPlayers):
        self.gameId = gameId
        self.events = matchEvents
        self.players = matchPlayers

        self.homeTeamName = matchTeams.iloc[0]["team_name"]
        self.homeTeamId = matchTeams.iloc[0]["team_id"]
        self.awayTeamName = matchTeams.iloc[1]["team_name"]
        self.awayTeamId = matchTeams.iloc[1]["team_id"]
        self.homeTeamColor = "#3f8ae6"
        self.awayTeamColor = "#f04a5f"

        self.teamNames = list([self.homeTeamName, self.awayTeamName])
        self.teamIdentifiers = list([self.homeTeamId, self.awayTeamId])
        self.teamColors = list([self.homeTeamColor, self.awayTeamColor])
