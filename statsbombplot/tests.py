import os
import json
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

from utils import Pitch, getStatsbombAPI, addLegend, addNotes, saveFigure, fetchMatch


api = getStatsbombAPI()

print(api.competitions())
