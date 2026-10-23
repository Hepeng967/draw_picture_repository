# -*- coding: utf-8 -*-
"""
ECharts: boxplot-multi（多系列盒须图）→ Matplotlib
原图：https://echarts.apache.org/examples/zh/editor.html?c=boxplot-multi
运行：python 04_boxplot_multi.py

JS 原代码会独立生成 3 个系列，每个系列有 18 个类别，每个类别含 100 个 [0,200) 观测值。
此处固定随机种子以保证研究/论文复现，JS 的 Math.random() 则每次都不同。
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch

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

NUM_SERIES = 3
NUM_CATEGORIES = 18
OBS_PER_CATEGORY = 100
SEED = 2026
COLORS = [LIGHT_FILL, "#8EF0FB", "#B8F6FD"]
USE_ECHARTS_YLIM = True  # 原图纵轴固定 [-400,600]，虽数据仅在 [0,200)。


def make_data():
    rng = np.random.default_rng(SEED)
    return rng.uniform(0, 200, size=(NUM_SERIES, NUM_CATEGORIES, OBS_PER_CATEGORY))


def draw(data: np.ndarray, selected_indices, filename: str):
    num = len(selected_indices)
    fig, ax = plt.subplots(figsize=(max(9.5, num * 0.78), 6.8))
    centers = np.arange(1, num + 1)
    width = 0.23
    for s in range(NUM_SERIES):
        positions = centers + (s - 1) * width
        series_samples = [data[s, i].tolist() for i in selected_indices]
        ax.boxplot(
            series_samples, positions=positions, widths=width * 0.83,
            whis=1.5, patch_artist=True, showfliers=True, manage_ticks=False,
            boxprops={"facecolor": COLORS[s], "edgecolor": LIGHT_LINE, "alpha": 0.72, "linewidth": 1.15},
            medianprops={"color": LIGHT_MEDIAN, "linewidth": 1.35},
            whiskerprops={"color": LIGHT_LINE, "linewidth": 1.1},
            capprops={"color": LIGHT_LINE, "linewidth": 1.1},
            flierprops={"marker": "o", "markerfacecolor": "none", "markeredgecolor": OUTLIER_LINE,
                        "markeredgewidth": 1.0, "markersize": 2.8},
        )

    ax.set_xticks(centers, [str(i) for i in selected_indices])
    ax.set_xlim(0.4, num + 0.6)
    if USE_ECHARTS_YLIM:
        ax.set_ylim(-400, 600)
    ax.set_ylabel("Value", fontweight="bold")
    ax.set_xlabel("Category", fontweight="bold")
    ax.set_title("Multiple Categories", fontsize=16, pad=26, fontweight="bold")
    ax.grid(axis="y", alpha=0.65, color="#e4e7ee")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight("bold")
    legend_handles = [Patch(facecolor=COLORS[i], edgecolor=LIGHT_LINE, alpha=0.8,
                            label=f"category{i}") for i in range(NUM_SERIES)]
    ax.legend(handles=legend_handles, loc="upper center", ncol=3,
              bbox_to_anchor=(0.5, 1.02), frameon=False,
              prop={"family": FONT_FAMILY, "weight": "bold", "size": 11})
    fig.tight_layout()
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{filename}.{ext}", dpi=300, bbox_inches="tight")
    print("完成：", OUT / f"{filename}.png")
    plt.close(fig)


if __name__ == "__main__":
    all_data = make_data()
    draw(all_data, list(range(NUM_CATEGORIES)), "04_boxplot_multi_full")
    # ECharts 原版 dataZoom start=0,end=20，初始仅显示约 20% 的类别。
    draw(all_data, list(range(4)), "04_boxplot_multi_zoom20")
