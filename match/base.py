from common import get_statsbomb_api
import os


class BaseSBP:
    def __init__(self):
        self.api = get_statsbomb_api()
        self.markerSize = 60
        self.lineWidth = 0.6
        self.fontSize = 8
        self.homeColor = "#42a5f5"
        self.awayColor = "#f76c5e"
