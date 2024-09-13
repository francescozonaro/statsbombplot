import pandas as pd

from elements.passingNetwork import PassingNetwork
from utils.common import changeRange, addAnnotations, saveFigure, addLegend


class Match:
    def __init__(self, gameId, matchEvents, matchTeams, matchPlayers):
        self.gameId = gameId
        self.events = matchEvents
        self.players = matchPlayers

        self.homeTeamName = matchTeams.iloc[0]["team_name"]
        self.homeTeamId = matchTeams.iloc[0]["team_id"]
        self.awayTeamName = matchTeams.iloc[1]["team_name"]
        self.awayTeamId = matchTeams.iloc[1]["team_id"]
        self.homeTeamColor = "#42a5f5"
        self.awayTeamColor = "#f76c5e"

        self.teamNames = list([self.homeTeamName, self.awayTeamName])
        self.teamIdentifiers = list([self.homeTeamId, self.awayTeamId])
        self.teamColors = list([self.homeTeamColor, self.awayTeamColor])

    def drawPassingNetworks(self):
        for identifier, markerColor, teamName in zip(
            self.teamIdentifiers, self.teamColors, self.teamNames
        ):
            teamEvents = self.events[self.events["team_id"] == identifier].copy()

            indexFirstSub = teamEvents[
                teamEvents.type_name == "Substitution"
            ].index.min()

            df = teamEvents[teamEvents.index < indexFirstSub]
            df = df[df.type_name == "Pass"]
            df = df[
                df["extra"].apply(lambda x: "pass" in x and "outcome" in x["pass"])
                == False
            ].reset_index(drop=True)
            df["receiver"] = df["extra"].apply(
                lambda x: x.get("pass", {}).get("recipient", {}).get("name")
            )
            df["location_end"] = df["extra"].apply(
                lambda x: x.get("pass", {}).get("end_location")
            )
            df[["x", "y"]] = pd.DataFrame(df["location"].tolist())
            df[["x_end", "y_end"]] = pd.DataFrame(df["location_end"].tolist())

            df["x"] = df["x"].apply(
                lambda value: changeRange(value, [0, 120], [0, 105])
            )
            df["y"] = 68 - df["y"].apply(
                lambda value: changeRange(value, [0, 80], [0, 68])
            )
            df["x_end"] = df["x_end"].apply(
                lambda value: changeRange(value, [0, 120], [0, 105])
            )
            df["y_end"] = df["y_end"].apply(
                lambda value: changeRange(value, [0, 80], [0, 68])
            )
            df = df[["player_name", "x", "y", "receiver", "x_end", "y_end"]]

            playerPassCount = df.groupby("player_name").size().to_frame("num_passes")
            df["pair_key"] = df.apply(
                lambda x: "_".join(sorted([x["player_name"], x["receiver"]])), axis=1
            )
            pairPassCount = df.groupby("pair_key").size().to_frame("num_passes")
            pairPassCount = pairPassCount[pairPassCount["num_passes"] > 3]
            playerPosition = df.groupby("player_name").agg({"x": "mean", "y": "mean"})

            passingNetwork = PassingNetwork(markerColor=markerColor)
            fig, ax, legendElements = passingNetwork.draw(
                playerPassCount, pairPassCount, playerPosition
            )

            extra_text = [
                "Player position is determined by the average location from which they passed the ball.",
                "Only events occurring prior to the first substitution are included in the analysis.",
            ]

            addLegend(ax, legendElements)
            addAnnotations(
                ax,
                author="@francescozonaro",
                extra_text=extra_text,
            )
            saveFigure(fig, f"imgs/passingNetwork_{self.gameId}_{teamName}.png")
