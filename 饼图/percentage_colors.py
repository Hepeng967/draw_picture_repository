"""百分比饼图专用色彩库。前七色取自参考图，后续自动扩展柔和色。"""

import colorsys
import math

from matplotlib.colors import to_hex, to_rgb


REFERENCE_COLORS = (
    "#B3E2CD", "#FDCDAC", "#CBD5E8", "#F4CAE4",
    "#E6F5C9", "#FFF2AE", "#F1E2CC",
)
EXTRA_COLORS = (
    "#B9DFF2", "#D9C8ED", "#F3BCC2", "#CCE5DD",
    "#E4DDB7", "#D3E0F4", "#F6D8C5", "#CCE8BA",
)


def get_colors(count: int) -> list[str]:
    """按输入顺序选色，不循环复用已有颜色。"""
    palette = list(REFERENCE_COLORS + EXTRA_COLORS)
    while len(palette) < count:
        # 从低饱和度、高亮度候选中选择与已有颜色差异最大的颜色。
        candidates = [
            colorsys.hls_to_rgb(h / 72, light, saturation)
            for h in range(72)
            for light in (0.79, 0.85, 0.9)
            for saturation in (0.40, 0.58, 0.72)
        ]
        existing = [to_rgb(c) for c in palette]
        color = max(candidates, key=lambda c: min(math.dist(c, old) for old in existing))
        palette.append(to_hex(color).upper())
    return palette[:count]
