class Match:
    def __init__(self, game_id, match_events, match_teams, match_players):
        self.game_id = game_id
        self.events = match_events
        self.players = match_players

        self.home_team_name = match_teams.iloc[0]["team_name"]
        self.home_team_id = match_teams.iloc[0]["team_id"]
        self.away_team_name = match_teams.iloc[1]["team_name"]
        self.away_team_id = match_teams.iloc[1]["team_id"]

        self.team_names = [self.home_team_name, self.away_team_name]
        self.team_ids = [self.home_team_id, self.away_team_id]
