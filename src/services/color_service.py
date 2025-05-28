import requests
from PIL import Image
import io
import colorgram


def rgb_to_hex(rgb):
    """Convert RGB tuple to HEX string."""
    return "#%02x%02x%02x" % rgb


def extract_ui_colors(url):
    """
    Extract primary, background, and up to 3 accent colors from a UI/UX design image URL.

    Args:
        url (str): URL of the image.

    Returns:
        dict: A dictionary with 'background' (HEX string), 'primary' (HEX string), and
              'accent' (list of up to 3 HEX strings). If fewer than 5 colors are extracted,
              only available colors are returned.
    """
    try:
        # Download the image from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Load the image using PIL
        image = Image.open(io.BytesIO(response.content))

        # Extract a color palette with 5 colors
        palette = colorgram.extract(image, 5)

        # Sort the palette by proportion (frequency)
        palette_sorted = sorted(palette, key=lambda c: c.proportion, reverse=True)

        # Assign roles to the colors
        result = {"accent": []}
        if len(palette_sorted) >= 1:
            result["background"] = rgb_to_hex(palette_sorted[0].rgb)
        if len(palette_sorted) >= 2:
            result["primary"] = rgb_to_hex(palette_sorted[1].rgb)
        if len(palette_sorted) >= 3:
            result["accent"].append(rgb_to_hex(palette_sorted[2].rgb))
        if len(palette_sorted) >= 4:
            result["accent"].append(rgb_to_hex(palette_sorted[3].rgb))
        if len(palette_sorted) >= 5:
            result["accent"].append(rgb_to_hex(palette_sorted[4].rgb))

        return result

    except Exception as e:
        print(f"Error: {e}")
        return None
