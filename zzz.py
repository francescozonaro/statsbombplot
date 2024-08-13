from utils import get_statsbomb_api
import pandas as pd

pd.set_option("display.max_rows", None)

MENU_OPTIONS = {
    1: "Generate a report",
    0: "Exit",
}


def print_menu():
    print("\n")
    for key, value in MENU_OPTIONS.items():
        print(f"{key} -- {value}")
    print("\n")


def main():

    api = get_statsbomb_api()

    while True:
        print_menu()
        try:
            option = int(input("\nEnter your choice: "))
        except ValueError:
            print()

        if option == 1:
            competitions = api.competitions()
            unique_competitions = (
                competitions[["competition_id", "competition_name"]]
                .drop_duplicates()
                .sort_values("competition_id")
                .reset_index(drop=True)
            )
            print(unique_competitions)

            try:
                comp_id = int(
                    input("\nEnter a valid competition id from the list (0 to exit): ")
                )
                if comp_id == 0:
                    print("Bye!")
                    exit()
            except:
                print()

            print(
                competitions[competitions["competition_id"] == comp_id]
                .sort_values("season_name")
                .reset_index(drop=True)
            )

            try:
                season_id = int(input("\nEnter a valid season_id (0 to exit): "))
                if season_id == 0:
                    print("Bye!")
                    exit()
            except:
                print()

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
                ]
            )

        elif option == 0:
            print("Bye!")
            exit()
        else:
            print("Invalid option.")


if __name__ == "__main__":

    main()
