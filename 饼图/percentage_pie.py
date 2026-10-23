"""百分比饼图：唯一输入为 JSON 路径，样式与配色由程序自动管理。"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from percentage_colors import get_colors
from chart_utils import load_records, number, name, shares, fonts, fit_text, text_size, save_chart


DEFAULT_JSON = Path(__file__).with_name("percentages.json")


def _read_percentages(json_path: str | Path) -> tuple[list[str], list[float]]:
    records = load_records(json_path)
    labels, values = [], []
    for i, record in enumerate(records):
        if set(record) - {"name", "value"}:
            raise ValueError(f"第 {i + 1} 项请只使用 name、value 字段。")
        labels.append(name(record.get("name"), f"Item {i + 1:02d}"))
        values.append(number(record.get("value"), f"第 {i + 1} 项 value"))
    return labels, shares(values)


def plot_percentage_pie(json_path: str | Path = DEFAULT_JSON) -> tuple:
    """只读取 JSON；返回 (figure, axes)。角度和百分比由同一组 value 计算。"""
    labels, fractions = _read_percentages(json_path)
    colors = get_colors(len(labels))
    active = [i for i, fraction in enumerate(fractions) if fraction > 0]
    legend_size = max(12, min(23, 23 * math.sqrt(10 / len(labels))))
    height = max(5.85, len(labels) * legend_size * 1.5 / 72 + 0.5)
    family = fonts(serif=True)
    # 参考图的最小 2% 扇区无标注；选项增多时自动降低隐藏阈值。
    threshold = min(3, 50 / len(active))
    decimals = 0 if all(abs(fractions[i]*100-round(fractions[i]*100)) < 1e-6 for i in active) else 1
    with plt.rc_context({"font.family": family, "axes.unicode_minus": False}):
        fig = plt.figure(figsize=(10, height), dpi=160, facecolor="white")
        ax = fig.add_axes((0.025, 0.04, 0.535, 0.92))
        ax.set_aspect("equal")
        wedges, _ = ax.pie(
            [fractions[i] for i in active], colors=[colors[i] for i in active],
            startangle=90, counterclock=True, explode=[0.035]*len(active),
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        )
        ax.set_xlim(-1.12, 1.12)
        ax.set_ylim(-1.12, 1.12)
        fig.canvas.draw()
        radius_px = ax.bbox.width / 2.24
        for wedge, i in zip(wedges, active):
            wedge.set_gid(f"slice-{i}")
            pct = fractions[i]*100
            if pct+1e-6 < threshold:
                continue
            theta = math.radians((wedge.theta1+wedge.theta2)/2)
            text = f"{pct:.{decimals}f}%"
            angle = min(180, wedge.theta2-wedge.theta1)
            available = 2*0.62*math.sin(math.radians(angle)/2)*radius_px
            size = fit_text(fig, text, 24, 0.7*radius_px,
                            max(1, available*0.9), family, bold=True)
            # 水平文字在上下方的扇区更容易横向越界；同时检查两条径向边界。
            width, text_height = text_size(fig, text, size, family, bold=True)
            half_angle = math.radians(angle) / 2
            distance = 0.62 * radius_px * math.sin(half_angle)
            projected = max(
                abs(math.sin(boundary))*width/2 + abs(math.cos(boundary))*text_height/2
                for boundary in (theta-half_angle, theta+half_angle)
            )
            if len(active) > 7:
                size *= min(1, 0.9 * distance / max(projected, 1))
            ax.text(wedge.center[0]+0.62*math.cos(theta),
                    wedge.center[1]+0.62*math.sin(theta), text,
                    ha="center", va="center", fontsize=size, fontweight="bold", color="#7F807F")
        legend = fig.legend(
            handles=[Patch(facecolor=c, edgecolor="white") for c in colors], labels=labels,
            loc="center left", bbox_to_anchor=(0.56, 0.5), fontsize=legend_size,
            frameon=True, fancybox=True, borderpad=0.3, labelspacing=0.35,
            handlelength=2, handletextpad=0.65,
        )
        legend.get_frame().set_edgecolor("#D5D6D5")
        legend.get_frame().set_linewidth(1.8)
        legend.get_frame().set_facecolor("white")
        return fig, ax


def draw_percentage_pie(json_path: str | Path = DEFAULT_JSON) -> Path:
    """读取一个 JSON，在项目 results 中生成 PNG、SVG、PDF，返回 PNG 路径。"""
    fig, _ = plot_percentage_pie(json_path)
    try:
        return save_chart(fig, json_path)
    finally:
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json", nargs="?", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    try:
        print(draw_percentage_pie(args.json))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"无法绘制百分比饼图：{exc}\n")


if __name__ == "__main__":
    main()
