class Match:
    def __init__(self, gameId, matchEvents, matchTeams, matchPlayers):
        self.gameId = gameId
        self.events = matchEvents
        self.players = matchPlayers

        self.homeTeamName = matchTeams.iloc[0]["team_name"]
        self.homeTeamId = matchTeams.iloc[0]["team_id"]
        self.awayTeamName = matchTeams.iloc[1]["team_name"]
        self.awayTeamId = matchTeams.iloc[1]["team_id"]
        self.homeTeamColor = "#e07a5f"
        self.awayTeamColor = "#8ecae6"

        self.teamNames = list([self.homeTeamName, self.awayTeamName])
        self.teamIdentifiers = list([self.homeTeamId, self.awayTeamId])
        self.teamColors = list([self.homeTeamColor, self.awayTeamColor])
