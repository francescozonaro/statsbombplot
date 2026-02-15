import random

from utils import getStatsbombAPI
from utils.commons import fetchMatch

matchesLength = 0
api = getStatsbombAPI()
df = api.competitions()
isValid = df["competition_name"] == "Premier League"
print(df[isValid])
