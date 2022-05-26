from typing import Tuple


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """

    :param h: [0, 360[
    :param s: [0, 1]
    :param v: [0, 1]
    :return: 3x ints in [0, 256[
    """
    # source: https://www.rapidtables.com/convert/color/hsv-to-rgb.html
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        rgb = (c, x, 0)
    elif h < 120:
        rgb = (x, c, 0)
    elif h < 180:
        rgb = (0, c, x)
    elif h < 240:
        rgb = (0, x, c)
    elif h < 300:
        rgb = (x, 0, c)
    else:   # h < 360
        rgb = (c, 0, x)
    r, g, b = rgb
    rgb = int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

    for val in rgb:
        if val < 0 or 256 <= val:
            raise ValueError(f"Illegal color value: {val}!")

    return rgb
