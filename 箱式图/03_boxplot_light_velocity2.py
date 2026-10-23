# -*- coding: utf-8 -*-
"""
ECharts: boxplot-light-velocity2（横向盒须图）→ Matplotlib
原图：https://echarts.apache.org/examples/zh/editor.html?c=boxplot-light-velocity2
运行：python 03_boxplot_light_velocity2.py
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

LIGHT_FILL = "#67E8F9"          # RGB(103, 232, 249)
LIGHT_LINE = "#78C5D1"          # 柔和的浅青色：箱体边线 / 须线 / 帽线
LIGHT_MEDIAN = "#4AA7B7"        # 中位数线略深，保留层次
OUTLIER_LINE = "#75B9C5"       # 空心圆的边线（无填充）

# 先检查本机字体：有 Times New Roman 则使用；没有则明确回退至
# Matplotlib 常见默认字体 DejaVu Sans，避免 findfont 警告。
AVAILABLE_FONT_NAMES = {item.name for item in font_manager.fontManager.ttflist}
FONT_FAMILY = "Times New Roman" if "Times New Roman" in AVAILABLE_FONT_NAMES else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT_FAMILY,
    "font.weight": "bold",
    "axes.labelweight": "bold",
    "axes.titleweight": "bold",
    "figure.titleweight": "bold",
})

# 与第二个示例完全相同的五组原始实验数据。
RAW_DATA = [
    [850, 740, 900, 1070, 930, 850, 950, 980, 980, 880, 1000, 980, 930, 650, 760, 810, 1000, 1000, 960, 960],
    [960, 940, 960, 940, 880, 800, 850, 880, 900, 840, 830, 790, 810, 880, 880, 830, 800, 790, 760, 800],
    [880, 880, 880, 860, 720, 720, 620, 860, 970, 950, 880, 910, 850, 870, 840, 840, 850, 840, 840, 840],
    [890, 810, 810, 820, 800, 770, 760, 740, 750, 760, 910, 920, 890, 860, 880, 720, 840, 850, 850, 780],
    [890, 840, 780, 810, 760, 810, 790, 810, 820, 850, 870, 870, 810, 740, 810, 940, 950, 800, 810, 870],
]


def draw():
    fig, ax = plt.subplots(figsize=(11, 6.6))
    # 用 vert=False 把箱线图转为水平，离群点自动定位。
    ax.boxplot(
        RAW_DATA, vert=False,
        tick_labels=[f"expr {i}" for i in range(len(RAW_DATA))],
        whis=1.5, widths=0.56, patch_artist=True, showfliers=True,
        boxprops={"facecolor": LIGHT_FILL, "edgecolor": LIGHT_LINE, "linewidth": 1.4},
        medianprops={"color": LIGHT_MEDIAN, "linewidth": 1.8},
        whiskerprops={"color": LIGHT_LINE, "linewidth": 1.3},
        capprops={"color": LIGHT_LINE, "linewidth": 1.3},
        flierprops={"marker": "o", "markerfacecolor": "none", "markeredgecolor": OUTLIER_LINE,
                    "markeredgewidth": 1.3, "markersize": 5.5},
    )
    ax.set_title("Michelson-Morley Experiment", fontsize=16, pad=20, fontweight="bold")
    ax.set_xlabel("km/s minus 299,000", fontsize=11, fontweight="bold")
    ax.grid(axis="x", color="#e6eaf1")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight("bold")
    fig.subplots_adjust(left=0.14, right=0.94, top=0.86, bottom=0.25)
    fig.text(0.14, 0.055, "upper: Q3 + 1.5 × IQR\nlower: Q1 − 1.5 × IQR",
             fontsize=10.5, fontweight="bold", linespacing=1.4,
             bbox={"facecolor": "white", "edgecolor": "#C1DDE2", "boxstyle": "square,pad=0.5"})
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"03_boxplot_light_velocity2.{ext}", dpi=300, bbox_inches="tight")
    print("完成：", OUT / "03_boxplot_light_velocity2.png")
    plt.close(fig)


if __name__ == "__main__":
    draw()
