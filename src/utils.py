import re


def extract_dribbble_query(markdown: str):
    """
    Extracts a list of result dicts from Dribbble markdown content.
    Each result contains title, description, image_urls, and url.
    Also extracts 'userupload' images from both image and empty-link markdown.
    """
    # Find all result blocks starting with a number and '![', ending before the next number or end of string
    blocks = re.findall(r"(\d+\. !\[.*?)(?=\n\s*\d+\. !\[|\Z)", markdown, re.DOTALL)
    results = []
    for block in blocks:
        m = re.match(r"\d+\. !\[(.*?)\]\((.*?)\) \[ View (.*?) \]\((.*?)\)", block)
        if not m:
            continue
        description = m.group(1)
        title = m.group(3)
        url = m.group(4)
        # Extract all userupload image URLs from both image and empty-link markdown in the block
        image_pattern = r"!\[.*?\]\((.*?)\)"
        empty_link_pattern = r"\[\]\((.*?)\)"
        image_urls = [
            img for img in re.findall(image_pattern, block) if "userupload" in img
        ]
        image_urls += [
            link
            for link in re.findall(empty_link_pattern, block)
            if "userupload" in link and link not in image_urls
        ]
        results.append(
            {
                "title": title,
                "description": description,
                "image_urls": image_urls,
                "url": url,
            }
        )
    return results


def extract_design_features(markdown: str):
    """
    Extracts color_palette (list of color code strings), image_urls (only those containing 'userupload'), and description from Dribbble markdown content.
    Returns a dict with keys: color_palette (list of color code strings),
    image_urls (list of image URLs containing 'userupload'), and description (str).
    Also extracts 'userupload' images from both image and empty-link markdown.
    """
    # Extract color palette: just the color codes (e.g., #C8D2DB)
    color_palette = [
        m.group(1)
        for m in re.finditer(r"\[(#(?:[0-9A-Fa-f]{6}))\]\(([^\)]+)\)", markdown)
    ]

    # Extract all userupload image URLs from both image and empty-link markdown
    image_pattern = r"!\[.*?\]\((.*?)\)"
    empty_link_pattern = r"\[\]\((.*?)\)"
    image_urls = [
        img for img in re.findall(image_pattern, markdown) if "userupload" in img
    ]
    image_urls += [
        link
        for link in re.findall(empty_link_pattern, markdown)
        if "userupload" in link and link not in image_urls
    ]

    # Extract description: look for a greeting and designer's note (e.g., after 'Hello')
    desc_match = re.search(
        r"Hello.*?(?:!|\n)(.*?)(?=\n\[|\n#|\n####|\n\Z)", markdown, re.DOTALL
    )
    description = desc_match.group(1).strip() if desc_match else ""

    return {
        "color_palette": color_palette,
        "image_urls": image_urls,
        "description": description,
    }
