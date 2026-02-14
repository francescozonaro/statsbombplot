import matplotlib.font_manager as fm

# List all available font families
font_paths = fm.findSystemFonts(fontpaths=None, fontext="ttf")
allFonts = []
for path in font_paths:
    try:
        font = fm.FontProperties(fname=path)
        name = font.get_name()
        allFonts.append(name)
    except Exception as e:
        print(f"Failed to load font at {path}: {e}")

print(sorted(allFonts))
