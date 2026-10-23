"""分类饼图专用色彩库：分类纯色与所属子项的渐变色。"""

import colorsys
import math

from matplotlib.colors import to_hex, to_rgb


REFERENCE_COLORS = (
    "#FDD663", "#7CB342", "#8AB4F8", "#B4A7D6", "#AECBFA", "#F28B82",
)
# 参考图外层顺时针渐变。数量变化时在这些色阶之间重新插值。
REFERENCE_GRADIENTS = (
    ("#FFFFA0", "#FFFF9C", "#FFFF9B", "#FFFF99", "#FFFF97", "#FFFB93",
     "#FFFA92", "#FFF790", "#FFF58E", "#FFF28B", "#FFF189", "#FFEE87",
     "#FFEB84", "#FFE982", "#FFE77F", "#FFE57E", "#FFE27B", "#FFE079",
     "#FFDE76", "#FFDC75", "#FCD972"),
    ("#90C05C", "#8BBE59", "#8BBD56", "#88BA54"),
    ("#A5CBFF", "#A3C8FF", "#A1C6FF", "#9EC4FF",
     "#9CC2FF", "#9ABFFC", "#98BDFB", "#94BBF8"),
    ("#CBBFE9", "#C8BDE7", "#C6BBE5", "#C4B7E2",
     "#C2B6E0", "#BFB4DE", "#BDB2DC", "#BBAED9"),
    ("#D7F2FF", "#D6F0FF", "#D3ECFF", "#D1EBFF", "#CFE9FF", "#CDE6FF",
     "#C9E3FF", "#C7E1FF", "#C6E0FF", "#C3DDFF", "#C0DAFF", "#BED8FF",
     "#BDD7FF", "#BAD4FF", "#B7D1FC", "#B5CFFA"),
    ("#FFD4CC", "#FFD1C8", "#FFCFC7", "#FFCDC5", "#FFCBC3", "#FFC8C0",
     "#FFC6BE", "#FFC4BC", "#FFC0B9", "#FFBFB7", "#FFBDB4", "#FFBBB3",
     "#FFB7B0", "#FFB6AE", "#FFB4AB", "#FFB2AA", "#FFAEA7", "#FFACA4",
     "#FFABA3", "#FFA8A0", "#FFA59E", "#FFA39B", "#FFA29A", "#FB9F97",
     "#FA9C94", "#F79A92", "#F59991", "#F2968E"),
)
EXTRA_COLORS = (
    "#79BFB2", "#E7AD72", "#C68FAE", "#94B6C8",
    "#AAB875", "#A28DC5", "#D3B58C", "#C18F89",
)


def get_colors(count: int) -> list[str]:
    palette = list(REFERENCE_COLORS + EXTRA_COLORS)
    while len(palette) < count:
        candidates = [
            colorsys.hls_to_rgb(h / 72, light, saturation)
            for h in range(72)
            for light in (0.62, 0.70, 0.78)
            for saturation in (0.40, 0.58, 0.72)
        ]
        existing = [to_rgb(c) for c in palette]
        color = max(candidates, key=lambda c: min(math.dist(c, old) for old in existing))
        palette.append(to_hex(color).upper())
    return palette[:count]


def get_child_colors(index: int, count: int, parent_color: str) -> list[str]:
    if index < len(REFERENCE_GRADIENTS):
        stops = [to_rgb(c) for c in REFERENCE_GRADIENTS[index]]
    else:
        base = to_rgb(parent_color)
        stops = [
            tuple(c + (1 - c) * 0.42 for c in base),
            tuple(c + (1 - c) * 0.08 for c in base),
        ]
    colors = []
    for i in range(count):
        position = (i / (count - 1) if count > 1 else 0.5) * (len(stops) - 1)
        left = min(int(position), len(stops) - 2)
        amount = position - left
        colors.append(to_hex(tuple(
            a + (b - a) * amount for a, b in zip(stops[left], stops[left + 1])
        )).upper())
    return colors
