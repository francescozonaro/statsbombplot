import pandas as pd
import os

from elements import PassingNetwork, ShotFrame
from utils.common import addNotes, saveFigure, addLegend


class Match:
    def __init__(self, gameId, matchEvents, matchTeams, matchPlayers):
        self.gameId = gameId
        self.events = matchEvents
        self.players = matchPlayers

        self.homeTeamName = matchTeams.iloc[0]["team_name"]
        self.homeTeamId = matchTeams.iloc[0]["team_id"]
        self.awayTeamName = matchTeams.iloc[1]["team_name"]
        self.awayTeamId = matchTeams.iloc[1]["team_id"]
        self.homeTeamColor = "#124559"
        self.awayTeamColor = "#61c089"

        self.teamNames = list([self.homeTeamName, self.awayTeamName])
        self.teamIdentifiers = list([self.homeTeamId, self.awayTeamId])
        self.teamColors = list([self.homeTeamColor, self.awayTeamColor])

        self.folder = f"imgs/{gameId}"
        os.makedirs(self.folder, exist_ok=True)

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

            df["y"] = 80 - df["y"]

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
            addNotes(
                ax,
                author="@francescozonaro",
                extra_text=extra_text,
            )
            saveFigure(
                fig, f"{self.folder}/passingNetwork_{self.gameId}_{teamName}.png"
            )

    def drawShotFrames(self):

        playerNameToJerseyNumber = self.players.set_index("player_name")[
            "jersey_number"
        ].to_dict()

        shots = self.events[self.events["type_name"] == "Shot"].reset_index(drop=True)

        for i, shot in shots.iterrows():

            if shot.team_id == self.homeTeamId:
                shotFreezed = ShotFrame(self.homeTeamColor, self.awayTeamColor)
            else:
                shotFreezed = ShotFrame(self.awayTeamColor, self.homeTeamColor)

            if shot["period_id"] < 5:
                if (
                    "extra" in shot
                    and "shot" in shot["extra"]
                    and "freeze_frame" in shot["extra"]["shot"]
                ):

                    fig, ax, legendElements = shotFreezed.draw(
                        shot,
                        playerNameToJerseyNumber,
                    )

                    shotOutcome = shot.extra["shot"]["outcome"]["name"].lower()
                    shotTechnique = shot.extra["shot"]["technique"]["name"].lower()
                    shotValue = shot.extra["shot"]["statsbomb_xg"]

                    if shotTechnique == "normal":
                        shotTechnique = shot.extra["shot"]["body_part"]["name"].lower()

                    extra = [
                        f"{shot.player_name} shot at {shot.minute}:{shot.second} with {shotTechnique} had an xG of {round(shotValue, 3)} and resulted in {shotOutcome}"
                    ]
                    addLegend(ax, legendElements)
                    addNotes(ax, author="@francescozonaro", extra_text=extra)
                    saveFigure(fig, f"{self.folder}/shotFreezed_{self.gameId}_{i}.png")
                else:
                    print(f"Skipping shot {i}: 'freeze_frame' not available.")
            else:
                print(f"Skipping shot {i}: Penalty shots are excluded.")
