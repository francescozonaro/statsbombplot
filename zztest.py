from PIL import Image


def replace_white(input_path, output_path, new_hex):
    # Convert hex to RGB
    new_color = tuple(int(new_hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))

    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if (r, g, b) == (255, 255, 255):
                pixels[x, y] = (*new_color, a)

    img.save(output_path)
    print(f"Saved to {output_path}")


from utils.config import *

# Usage
replace_white("input.png", "output.png", FIG_BACKGROUND_COLOR)
