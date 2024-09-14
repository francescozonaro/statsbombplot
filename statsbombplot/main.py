from utils import getStatsbombAPI
from match import Match
from teamSeason import TeamSeason
from requests.exceptions import HTTPError

import pandas as pd

pd.set_option("display.max_rows", None)

MENU_OPTIONS = {
    1: "Generate a new match report",
    2: "Generate a new season report",
    0: "Exit",
}

REPORT_OPTIONS = {
    1: "Draw passing networks",
    2: "Draw shot frames",
    0: "Exit",
}

SEASON_OPTIONS = {
    1: "Draw all shot frames",
    0: "Exit",
}

DEFAULT_GAME_ID = 3879868
STATSBOMB_API = getStatsbombAPI()


def print_menu(options):
    print("\n")
    for key, value in options.items():
        print(f"{key} -- {value}")
    print("\n")


def select_valid_id(df, id_column, display_columns, prompt, exit_value=0):
    while True:
        print(df[display_columns].to_string(index=False))
        selected_id = int(input(f"\n{prompt} ({exit_value} to exit): "))
        if selected_id == exit_value:
            print("Bye!")
            exit()
        if selected_id not in df[id_column].values:
            print("Invalid ID. Please try again.")
        else:
            return selected_id


def select_season():
    competitions = STATSBOMB_API.competitions()
    unique_competitions = (
        competitions[["competition_id", "competition_name"]]
        .drop_duplicates()
        .sort_values("competition_id")
        .reset_index(drop=True)
    )

    comp_id = select_valid_id(
        df=unique_competitions,
        id_column="competition_id",
        display_columns=["competition_id", "competition_name"],
        prompt="Enter a valid competition id from the list",
    )

    selected_competition = competitions[competitions["competition_id"] == comp_id]

    season_id = select_valid_id(
        df=selected_competition,
        id_column="season_id",
        display_columns=["season_id", "season_name"],
        prompt="Enter a valid season_id",
    )
    return comp_id, season_id


def select_match():
    comp_id, season_id = select_season()

    games = STATSBOMB_API.games(
        competition_id=comp_id, season_id=season_id
    ).sort_values("game_id")

    game_id = select_valid_id(
        df=games,
        id_column="game_id",
        display_columns=[
            "game_id",
            "game_date",
            "home_team_name",
            "away_team_name",
            "home_score",
            "away_score",
        ],
        prompt="Enter a valid game_id",
    )

    return game_id


def select_season_matches():
    comp_id, season_id = select_season()

    # Fetch games data from the StatsBomb API
    games = STATSBOMB_API.games(
        competition_id=comp_id, season_id=season_id
    ).sort_values("game_id")

    # Get a list of all unique teams playing in this season
    teams = sorted(
        set(
            list(games["home_team_name"].unique())
            + list(games["away_team_name"].unique())
        )
    )

    while True:
        print("Select one of the available teams (enter the ID):")
        for i, team in enumerate(teams, start=1):
            print(f"{i}. {team}")
        print("0. Exit")

        # Get user input to select a team by ID
        try:
            selection = int(input("Enter your choice (ID): "))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if selection == 0:
            print("Exiting...")
            return None

        if 1 <= selection <= len(teams):
            selectedTeam = teams[selection - 1]
            filteredGames = games[
                (games["home_team_name"] == selectedTeam)
                | (games["away_team_name"] == selectedTeam)
            ]
            print(f"Selected team: {selectedTeam}")
            print(filteredGames)

            seasonName = filteredGames["season_name"].unique()
            competitionName = filteredGames["competition_name"].unique()

            return (
                filteredGames["game_id"],
                competitionName[0],
                seasonName[0].replace("/", "-"),
                selectedTeam,
            )
        else:
            print("Please select a valid team ID.")


def main():

    while True:

        print_menu(MENU_OPTIONS)

        try:
            option = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input.")
            continue

        if option == 1:

            # gameId = select_match()
            gameId = DEFAULT_GAME_ID

            try:
                matchEvents = STATSBOMB_API.events(gameId, load_360=True)
            except HTTPError:
                print(f"No 360 data available for this match. Loading basic data.")
                matchEvents = STATSBOMB_API.events(gameId, load_360=False)

            players = STATSBOMB_API.players(gameId)
            teams = STATSBOMB_API.teams(gameId)
            match = Match(gameId, matchEvents, teams, players, folder=f"imgs/{gameId}")

            while True:
                print_menu(REPORT_OPTIONS)
                choice = int(input("Enter your choice: "))
                if choice == 1:
                    match.drawPassingNetworks()
                elif choice == 2:
                    match.drawShotFrames()
                elif choice == 0:
                    break
                else:
                    print("Invalid choice, please enter a valid number.")

        elif option == 2:
            gameIds, competitionName, seasonName, teamName = select_season_matches()
            teamSeason = TeamSeason(gameIds, competitionName, seasonName, teamName)

            while True:
                print_menu(SEASON_OPTIONS)
                choice = int(input("Enter your choice: "))
                if choice == 1:
                    teamSeason.drawTeamSeasonShotFrames()
                elif choice == 0:
                    break
                else:
                    print("Invalid choice, please enter a valid number.")

        elif option == 0:
            print("Bye!")
            exit()
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
