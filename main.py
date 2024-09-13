from utils import get_statsbomb_api
from match import (
    ScatterplotSBP,
    ProgressiveSBP,
    ShotmapSBP,
    ShotfreezedSBP,
    GoalBreakdownSBP,
    PassingNetworkSBP,
    BaseMatchSBP,
)
import pandas as pd

pd.set_option("display.max_rows", None)

MENU_OPTIONS = {
    1: "Generate a new match report",
    0: "Exit",
}

REPORT_OPTIONS = {
    1: "Draw scatterplots",
    2: "Draw progressive",
    3: "Draw shotmap",
    4: "Draw shot-frames",
    5: "Draw goal breakdowns",
    6: "Draw passing network",
    0: "Exit",
}

DEFAULT_GAME_ID = 3795506
STATSBOMB_API = get_statsbomb_api()


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

            # game_id = select_match()
            game_id = DEFAULT_GAME_ID

            events = STATSBOMB_API.events(game_id, load_360=True)
            players = STATSBOMB_API.players(game_id)
            teams = STATSBOMB_API.teams(game_id)

            base = BaseMatchSBP(game_id, events, teams, players)

            while True:
                print_menu(REPORT_OPTIONS)
                choice = int(input("Enter your choice: "))

                if choice == 1:
                    modes = ["defensive", "passing"]
                    scatterplot = ScatterplotSBP(base)
                    for mode in modes:
                        scatterplot.draw(mode)
                elif choice == 2:
                    progressive = ProgressiveSBP(base)
                    progressive.draw()
                elif choice == 3:
                    shotmap = ShotmapSBP(base)
                    shotmap.draw()
                elif choice == 4:
                    shotfreeze = ShotfreezedSBP(base)
                    shotfreeze.draw()
                elif choice == 5:
                    goalBreakdown = GoalBreakdownSBP(base)
                    goalBreakdown.draw()
                elif choice == 6:
                    passingNetwork = PassingNetworkSBP(base)
                    passingNetwork.draw()
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
