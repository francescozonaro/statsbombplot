import os
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

from utils import (
    Pitch,
    getStatsbombAPI,
    addLegend,
    addNotes,
    saveFigure,
    fetchMatch,
    featchAllSeasonMatches,
)

competitionId = 12
seasonId = 27
load_360 = True
folder = os.path.join("imgs/", str(gameId))
match = fetchMatch(gameId, load_360)
os.makedirs(folder, exist_ok=True)
