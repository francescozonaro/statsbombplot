class BaseMatchSBP:
    def __init__(self, game_id, events, teams, players):
        # self.markerSize = 60
        # self.lineWidth = 0.6
        # self.fontSize = 8
        self.game_id = game_id
        self.events = events
        self.teams = teams
        self.players = players
        self.set_team_info()

    def set_team_info(self):
        self.home_team_name = self.teams.iloc[0]["team_name"]
        self.away_team_name = self.teams.iloc[1]["team_name"]
        self.home_team_id = self.teams.iloc[0]["team_id"]
        self.away_team_id = self.teams.iloc[1]["team_id"]
        self.home_team_color = "#42a5f5"
        self.away_team_color = "#f76c5e"
