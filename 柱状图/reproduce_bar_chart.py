"""复现参考图的三个柱状图。

安装依赖：python -m pip install matplotlib numpy
运行脚本：python reproduce_bar_chart.py
输出文件保存在本脚本所在目录的 bar_chart_output 文件夹。

说明：颜色取自参考图的实心区域；数值和误差为截图估读值，不是原始数据。
截图不能唯一确定字体，默认用 Arial（图表）和 Segoe UI（标题）匹配。
三个纵轴均按参考图截断；柱高的视觉比例不能当作从零开始的比例。
误差类型（标准差/标准误/置信区间）无法从截图确定，正式使用请替换。
"""

from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")  # 无界面运行并保存图片；不需要打开绘图窗口。
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch
from matplotlib.ticker import FormatStrFormatter
import numpy as np


# ==================== 1. 数据配置区（主要修改这里） ====================
# 每一行对应一个模型，也就是每个子图中同一颜色的柱子。
# values 的顺序固定为：[AUROC, AUPRC, Mean PPVn]。
# errors 的顺序相同，表示柱顶上下对称误差线的半长度。
# 例如把 Prime-2.1 的 AUROC 改为 0.600：修改第一行 values 的第一个数。
# 若某根柱子不需要误差，可将其 error 设为 0；全部隐藏见 SHOW_ERROR_BARS。
MODELS = [
    dict(name="Prime-2.1",           color="#CFCECE", values=[0.538, 0.212, 0.207], errors=[0.012, 0.031, 0.013]),
    dict(name="NetMHCpan",           color="#F4EEAC", values=[0.537, 0.214, 0.220], errors=[0.027, 0.020, 0.008]),
    dict(name="MHCnuggets",          color="#FBDFE2", values=[0.546, 0.247, 0.233], errors=[0.023, 0.019, 0.014]),
    dict(name="MHCflurry",           color="#D9B9D4", values=[0.577, 0.261, 0.273], errors=[0.021, 0.026, 0.012]),
    dict(name="DeepNeo",             color="#DAA87C", values=[0.767, 0.439, 0.411], errors=[0.032, 0.024, 0.007]),
    dict(name="BigMHC-EL",           color="#DDF3DE", values=[0.588, 0.269, 0.290], errors=[0.018, 0.016, 0.011]),
    dict(name="BigMHC-IM",           color="#AADCA9", values=[0.684, 0.319, 0.333], errors=[0.028, 0.048, 0.015]),
    dict(name=r"BigMHC$_{\mathrm{retrained}}$", color="#8BCF8B", values=[0.793, 0.463, 0.445], errors=[0.013, 0.027, 0.004]),
    dict(name="ImmunoStruct (ours)", color="#3775BA", values=[0.882, 0.696, 0.514], errors=[0.005, 0.020, 0.009]),
]

# ==================== 2. 坐标轴与外观配置区 ====================
# 修改数据后，如果柱子或误差超过 ylim，请同时修改 ylim 和 ticks。
PANELS = [
    dict(label="AUROC",     ylim=(0.50, 0.90), ticks=[0.5, 0.6, 0.7, 0.8, 0.9]),
    dict(label="AUPRC",     ylim=(0.15, 0.75), ticks=[0.2, 0.3, 0.4, 0.5, 0.6, 0.7]),
    dict(label="Mean PPVn", ylim=(0.18, 0.55), ticks=[0.2, 0.3, 0.4, 0.5]),
]
TITLE = "Bar plots for quantitative comparison"
FONT_FAMILY = "Arial"
TITLE_FONT_FAMILY = "Segoe UI"
TITLE_FONT_SIZE = 37.5
LABEL_FONT_SIZE = 24
TICK_FONT_SIZE = 18
LEGEND_FONT_SIZE = 18
BAR_WIDTH = 0.80           # 柱宽，相邻柱子中心间距为 1。
SHOW_ERROR_BARS = True
CANVAS_SIZE = (22.21, 6.44)  # 英寸；100 dpi 时输出 2221 × 644 像素。
PNG_DPI = 100              # 可改为 300，字体与布局比例不变。
OUTPUT_DIR = Path(__file__).resolve().parent / "bar_chart_output"


def choose_font(preferred):
    """字体缺失时明确提示，避免误以为已精确使用指定字体。"""
    try:
        font_manager.findfont(preferred, fallback_to_default=False)
        return preferred
    except ValueError:
        warnings.warn(f"未安装字体 {preferred}，改用 DejaVu Sans；如需匹配请安装原字体。")
        return "DejaVu Sans"


def main():
    chart_font = choose_font(FONT_FAMILY)
    title_font = choose_font(TITLE_FONT_FAMILY)
    plt.rcParams.update({
        "font.family": chart_font,
        "mathtext.fontset": "custom",
        "mathtext.rm": chart_font,
        "mathtext.it": f"{chart_font}:italic",
        "mathtext.bf": f"{chart_font}:bold",
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,       # PDF 嵌入 TrueType 字体。
        "svg.fonttype": "none",  # SVG 保留可编辑文字。
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })

    values = np.array([m["values"] for m in MODELS], dtype=float)
    errors = np.array([m["errors"] for m in MODELS], dtype=float)
    if values.shape != (len(MODELS), 3) or errors.shape != values.shape:
        raise ValueError("每个模型的 values 和 errors 都必须包含 3 个数字。")
    if not np.isfinite(values).all() or not np.isfinite(errors).all() or (errors < 0).any():
        raise ValueError("数值必须是有限数，误差必须大于或等于 0。")

    fig = plt.figure(figsize=CANVAS_SIZE, dpi=PNG_DPI)
    # 使用参考图的像素位置换算布局，保留大标题和右侧图例空间。
    fig.text(63 / 2221, 1 - 95 / 644, TITLE,
             fontfamily=title_font, fontsize=TITLE_FONT_SIZE,
             fontweight="semibold", color="#1F2328", va="center")

    x = np.arange(len(MODELS))
    for j, (left, panel) in enumerate(zip([189, 702, 1214], PANELS)):
        ax = fig.add_axes([left / 2221, 95 / 644, 386 / 2221, 327 / 644])
        y = values[:, j]
        err = errors[:, j]
        lo, hi = panel["ylim"]
        lower = y - err if SHOW_ERROR_BARS else y
        upper = y + err if SHOW_ERROR_BARS else y
        if (lower < lo).any() or (upper > hi).any():
            warnings.warn(f"{panel['label']} 的数据或误差超过纵轴范围，请调整 PANELS 中的 ylim。")

        ax.bar(x, y, width=BAR_WIDTH, color=[m["color"] for m in MODELS],
               edgecolor="none", linewidth=0,
               yerr=err if SHOW_ERROR_BARS else None,
               error_kw={"ecolor": "black", "elinewidth": 0.8,
                         "capsize": 3.5, "capthick": 0.7})
        ax.set_ylim(lo, hi)
        ax.set_yticks(panel["ticks"])
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        ax.set_ylabel(panel["label"], fontsize=LABEL_FONT_SIZE, labelpad=1)
        ax.set_xlim(-0.85, len(MODELS) - 0.15)
        ax.set_xticks([])  # 与原图一致，通过图例识别模型，不显示横轴文字。
        ax.tick_params(axis="y", labelsize=TICK_FONT_SIZE, length=3, width=0.8, pad=2)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_linewidth(2.2)
        ax.grid(False)

    # 三个子图共用右侧图例，颜色与数据行一一对应。
    handles = [Patch(facecolor=m["color"], edgecolor="none", label=m["name"]) for m in MODELS]
    legend = fig.legend(handles=handles, loc="upper left",
                        bbox_to_anchor=(1782 / 2221, 1 - 234 / 644),
                        borderaxespad=0, fontsize=LEGEND_FONT_SIZE,
                        handlelength=2, handletextpad=0.8,
                        labelspacing=0.50, borderpad=0.4,
                        frameon=True, fancybox=True, framealpha=1,
                        facecolor="white", edgecolor="#CCCCCC")
    legend.get_frame().set_linewidth(0.6)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # 不使用 bbox_inches='tight'，避免改变参考图的画布尺寸和留白。
    for extension in ("png", "pdf", "svg"):
        destination = OUTPUT_DIR / f"reproduced_bar_chart.{extension}"
        fig.savefig(destination, dpi=PNG_DPI, facecolor="white")
        print(f"已保存：{destination}")
    plt.close(fig)


if __name__ == "__main__":
    main()
