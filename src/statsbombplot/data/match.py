import pandas as pd


class Match:
    """A single game: its events, players and the two teams (home first)."""

    def __init__(
        self,
        game_id: int,
        match_events: pd.DataFrame,
        match_teams: pd.DataFrame,
        match_players: pd.DataFrame,
    ) -> None:
        self.game_id = game_id
        self.events = match_events
        self.players = match_players

        self.home_team_name = match_teams.iloc[0]["team_name"]
        self.home_team_id = match_teams.iloc[0]["team_id"]
        self.away_team_name = match_teams.iloc[1]["team_name"]
        self.away_team_id = match_teams.iloc[1]["team_id"]

        self.team_names = [self.home_team_name, self.away_team_name]
        self.team_ids = [self.home_team_id, self.away_team_id]
