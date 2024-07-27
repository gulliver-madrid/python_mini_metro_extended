import colorsys

from src.type import Color


def reduce_saturation(rgb_color: Color, reduction_factor: float = 0.5) -> Color:
    # Convert RGB to range [0, 1]
    r, g, b = [x / 255.0 for x in rgb_color]

    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    # Reduce saturation
    s *= reduction_factor

    # Convert HLS back to RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    # Convert RGB back to range [0, 255]
    return (int(r * 255), int(g * 255), int(b * 255))
