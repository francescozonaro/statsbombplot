import pandas as pd
import pytest

from statsbombplot import cli

COMPETITIONS = pd.DataFrame(
    {
        "competition_id": [2, 2, 55],
        "season_id": [27, 26, 43],
        "competition_name": ["Premier League", "Premier League", "UEFA Euro"],
        "country_name": ["England", "England", "Europe"],
        "competition_gender": ["male", "male", "male"],
        "season_name": ["2015/2016", "2014/2015", "2020"],
    }
)

GAMES = pd.DataFrame(
    {
        "game_id": [11, 10],
        "game_date": pd.to_datetime(["2016-01-02 15:00", "2015-09-19 11:45"]),
        "game_day": [20, 6],
        "competition_stage": ["Regular Season", "Regular Season"],
        "home_team_name": ["Chelsea", "Arsenal"],
        "away_team_name": ["Everton", "Chelsea"],
        "home_score": [3, 0],
        "away_score": [3, 2],
    }
)


@pytest.fixture
def terminal(monkeypatch):
    """Pretend we are in a terminal and feed scripted answers to every prompt."""

    def feed(*answers):
        replies = iter(answers)
        monkeypatch.setattr(cli, "is_interactive", lambda: True)
        monkeypatch.setattr("builtins.input", lambda _: next(replies))

    monkeypatch.setattr(cli, "get_competitions", lambda: COMPETITIONS)
    monkeypatch.setattr(cli, "get_games", lambda competition_id, season_id: GAMES)
    return feed


def test_choose_by_number(terminal):
    terminal("2")
    assert cli.choose("Pick:", [("a", "A"), ("b", "B")]) == "b"


def test_choose_filters_by_text_and_treats_out_of_range_numbers_as_text(terminal):
    terminal("9", "bra", "1")
    assert cli.choose("Pick:", [("a", "Argentina"), ("b", "Brazil"), ("c", "Chile")]) == "b"


def test_choose_filters_by_year(terminal):
    terminal("2015", "1")
    assert cli.choose("Pick:", [("a", "2014/2015"), ("b", "2016/2017")]) == "a"


def test_choose_skips_prompt_with_a_single_option(terminal):
    terminal()  # any prompt would raise StopIteration
    assert cli.choose("Pick:", [("only", "Only one")]) == "only"


def test_season_given_on_command_line_is_not_prompted(terminal):
    terminal()
    assert cli.resolve_season(2, 27) == (2, 27)


def test_season_menu_only_offers_seasons_of_the_chosen_competition(terminal, capsys):
    terminal("1")  # newest season first
    assert cli.resolve_season(2, None) == (2, 27)
    out = capsys.readouterr().out
    assert "2015/2016" in out and "2014/2015" in out and "2020" not in out


def test_unknown_season_is_rejected(terminal):
    terminal()
    with pytest.raises(SystemExit, match="no open data"):
        cli.resolve_season(2, 43)


def test_full_walk_to_a_game_shows_date_gameweek_and_score(terminal, capsys):
    terminal("1", "1", "2")  # Premier League -> 2015/2016 -> second game by date
    assert cli.resolve_game(None) == 11
    out = capsys.readouterr().out
    assert "2015-09-19 · GW 6 · Arsenal 0-2 Chelsea" in out


def test_tournament_games_show_their_stage_instead_of_a_gameweek():
    row = next(GAMES.assign(competition_stage="Final").head(1).itertuples())
    assert " · Final · " in cli._game_label(row)


def test_game_id_flag_skips_every_prompt(terminal):
    terminal()
    assert cli.resolve_game(3795506) == 3795506


def test_missing_values_without_a_terminal_name_the_flags(monkeypatch):
    monkeypatch.setattr(cli, "is_interactive", lambda: False)
    monkeypatch.setattr(cli, "get_competitions", lambda: COMPETITIONS)
    with pytest.raises(SystemExit, match="--game-id"):
        cli.resolve_game(None)
    with pytest.raises(SystemExit, match="--season-id"):
        cli.resolve_season(2, None)
