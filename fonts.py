import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# List all available font families
font_paths = fm.findSystemFonts(fontpaths=None, fontext="ttf")
font_names = [fm.FontProperties(fname=path).get_name() for path in font_paths]

# Print a sorted list of font families
sorted(font_names)
print(font_names)
