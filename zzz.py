from common import get_statsbomb_api
from match import (
    ScatterplotSBP,
    ProgressiveSBP,
    ShotmapSBP,
    ShotfreezedSBP,
    # GoalBreakdownSB,
    # PassingNetworkSB,
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


def select_match():
    competitions = STATSBOMB_API.competitions()
    unique_competitions = (
        competitions[["competition_id", "competition_name"]]
        .drop_duplicates()
        .sort_values("competition_id")
        .reset_index(drop=True)
    )

    try:
        print(unique_competitions.to_string(index=False))
        comp_id = int(
            input("\nEnter a valid competition id from the list (0 to exit): ")
        )
        if comp_id == 0:
            print("Bye!")
            exit()
    except ValueError:
        print("Invalid input. Exiting.")
        exit()

    try:
        print(
            competitions[competitions["competition_id"] == comp_id]
            .sort_values("season_name")
            .reset_index(drop=True)
            .to_string(index=False)
        )
        season_id = int(input("\nEnter a valid season_id (0 to exit): "))
        if season_id == 0:
            print("Bye!")
            exit()
    except ValueError:
        print("Invalid input. Exiting.")
        exit()

    games = STATSBOMB_API.games(competition_id=comp_id, season_id=season_id)

    print(
        games[
            [
                "game_id",
                "game_date",
                "home_team_name",
                "away_team_name",
                "home_score",
                "away_score",
            ]
        ].to_string(index=False)
    )

    try:
        game_id = int(input("\nEnter a valid game_id (0 to exit): "))
        if game_id == 0:
            print("Bye!")
            exit()
        return game_id
    except ValueError:
        print("Invalid input. Exiting.")
        exit()


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
            teams["isHome"] = [True, False]

            print(teams)

            while True:
                print_menu(REPORT_OPTIONS)
                choice = int(input("Enter your choice: "))

                if choice == 1:
                    modes = ["defensive", "passing"]
                    scatterplot = ScatterplotSBP()
                    for mode in modes:
                        scatterplot.draw(game_id, events, teams, mode)
                elif choice == 2:
                    progressive = ProgressiveSBP()
                    progressive.draw(game_id, events, teams, players)
                elif choice == 3:
                    shotmap = ShotmapSBP()
                    shotmap.draw(game_id, events, teams)
                elif choice == 4:
                    shotfreeze = ShotfreezeSBP()
                    shotfreeze.draw(game_id, events, players)
                # elif choice == 5:
                #     gbs = GoalBreakdownSB()
                #     gbs.draw(game_id)
                # elif choice == 6:
                #     passingNetwork = PassingNetworkSB()
                #     passingNetwork.draw(game_id)
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
