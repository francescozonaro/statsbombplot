from utils import getStatsbombAPI
from match import Match
from requests.exceptions import HTTPError

import pandas as pd

pd.set_option("display.max_rows", None)

MENU_OPTIONS = {
    1: "Generate a new match report",
    0: "Exit",
}

REPORT_OPTIONS = {
    1: "Draw passing networks",
    2: "Draw shot frames",
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


def select_match():
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

            match = Match(gameId, matchEvents, teams, players)

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

        elif option == 0:
            print("Bye!")
            exit()
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
