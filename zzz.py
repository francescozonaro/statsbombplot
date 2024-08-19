from common import get_statsbomb_api
from match import (
    ScatterplotSB,
    ProgressiveSB,
    ShotmapSB,
    ShotframeSB,
    GoalBreakdownSB,
    PassingNetworkSB,
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


def print_menu(options):
    print("\n")
    for key, value in options.items():
        print(f"{key} -- {value}")
    print("\n")


def select_match():
    api = get_statsbomb_api()
    competitions = api.competitions()
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

    games = api.games(competition_id=comp_id, season_id=season_id)

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

            while True:
                print_menu(REPORT_OPTIONS)
                choice = int(input("Enter your choice: "))

                if choice == 1:
                    scatterplot_modes = ["defensive", "passing"]
                    scatterplot = ScatterplotSB()
                    for scatterplot_mode in scatterplot_modes:
                        scatterplot.draw(game_id, mode=scatterplot_mode)
                elif choice == 2:
                    progressive = ProgressiveSB()
                    progressive.draw(game_id)
                elif choice == 3:
                    shotmap = ShotmapSB()
                    shotmap.draw(game_id)
                elif choice == 4:
                    shotframe = ShotframeSB()
                    shotframe.draw(game_id)
                elif choice == 5:
                    gbs = GoalBreakdownSB()
                    gbs.draw(game_id)
                elif choice == 6:
                    passingNetwork = PassingNetworkSB()
                    passingNetwork.draw(game_id)
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
