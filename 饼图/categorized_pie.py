"""分类饼图：唯一输入为 JSON 路径，样式与配色由程序自动管理。"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

from categorized_colors import get_colors, get_child_colors
from chart_utils import load_records, number, name, shares, fonts, fit_text, save_chart


DEFAULT_JSON = Path(__file__).with_name("categories.json")


def _read_categories(json_path: str | Path) -> list[dict]:
    records = load_records(json_path)
    groups = []
    for i, record in enumerate(records):
        unexpected = set(record) - {"name", "value", "children"}
        if unexpected:
            raise ValueError(f"第 {i + 1} 类包含未知字段 {sorted(unexpected)}；请使用 name、value、children。")
        parent_value = number(record.get("value"), f"第 {i + 1} 类 value")
        children = record.get("children")
        if children is None:
            children = [{}]
        if not isinstance(children, list) or not children:
            raise ValueError(f"第 {i + 1} 类 children 必须为非空数组。")
        labels, weights = [], []
        for j, child in enumerate(children):
            if isinstance(child, str):
                child = {"name": child}
            if not isinstance(child, dict) or set(child) - {"name", "value"}:
                raise ValueError(f"第 {i + 1} 类的第 {j + 1} 个子项必须为名称字符串或 name/value 对象。")
            labels.append(name(child.get("name"), f"Item {j + 1:02d}"))
            weights.append(number(child.get("value"), f"第 {i + 1} 类 children[{j}] value"))
        child_shares = shares(weights, f"第 {i + 1} 类的子项") if parent_value > 0 else [0.0] * len(weights)
        groups.append({
            "index": i,
            "name": name(record.get("name"), f"Category {i + 1}"),
            "value": parent_value,
            "children": list(zip(labels, child_shares)),
        })
    fractions = shares([group["value"] for group in groups], "分类 value")
    for group, fraction in zip(groups, fractions):
        group["share"] = fraction
    return groups


def plot_categorized_pie(json_path: str | Path = DEFAULT_JSON) -> tuple:
    """只读取 JSON；返回 (figure, axes)。分类 value 决定总角度，子项在类内分配。"""
    groups = _read_categories(json_path)
    palette = get_colors(len(groups))
    active = [group for group in groups if group["share"] > 0]
    item_count = sum(sum(weight > 0 for _, weight in g["children"]) for g in active)
    side = min(24, max(10, 10 * math.sqrt(item_count / 85), 10 * math.sqrt(len(active) / 12)))
    family = fonts()
    radius = 0.535
    with plt.rc_context({"font.family": family, "axes.unicode_minus": False}):
        fig, ax = plt.subplots(figsize=(side, side), dpi=160, facecolor="white")
        fig.subplots_adjust(left=0.035, right=0.965, bottom=0.035, top=0.965)
        ax.set_aspect("equal")
        ax.set_xlim(-1.01, 1.01)
        ax.set_ylim(-1.01, 1.01)
        ax.axis("off")
        fig.canvas.draw()
        radius_px = ax.bbox.width / 2.02
        cursor = 139.76470588235293
        outer_labels, inner_labels = [], []
        # 父子共用角度边界，避免分别归一化造成边界错位。
        for group in active:
            end = cursor - 360 * group["share"]
            children = [(label, share) for label, share in group["children"] if share > 0]
            color = palette[group["index"]]
            child_colors = get_child_colors(group["index"], len(children), color)
            child_start = cursor
            for j, ((label, fraction), child_color) in enumerate(zip(children, child_colors)):
                child_end = end if j == len(children) - 1 else child_start - (cursor - end) * fraction
                wedge = Wedge((0, 0), 1, child_end, child_start, width=1-radius,
                              facecolor=child_color, edgecolor="white", linewidth=0.9)
                wedge.set_gid(f"child-{group['index']}-{j}")
                ax.add_patch(wedge)
                outer_labels.append((label, child_end, child_start))
                child_start = child_end
            wedge = Wedge((0, 0), radius, end, cursor, facecolor=color,
                          edgecolor="white", linewidth=0.9)
            wedge.set_gid(f"category-{group['index']}")
            ax.add_patch(wedge)
            inner_labels.append((group["name"], group["share"], end, cursor))
            cursor = end

        for label, begin, end in outer_labels:
            mid = (begin + end) / 2 % 360
            left = 90 < mid < 270
            theta = math.radians(mid)
            text_radius = radius + 0.017
            max_height = 2 * 0.72 * math.sin(math.radians(min(end-begin, 180)) / 2) * radius_px
            size = fit_text(fig, label, 15, (1-text_radius-0.025)*radius_px,
                            max_height, family)
            ax.text(text_radius*math.cos(theta), text_radius*math.sin(theta), label,
                    fontsize=size, rotation=mid+(180 if left else 0),
                    rotation_mode="anchor", ha="right" if left else "left", va="center")
        for label, fraction, begin, end in inner_labels:
            mid = (begin + end) / 2 % 360
            theta = math.radians(mid)
            crowded = len(active) > 6
            one_line = not crowded and end-begin < 40 and len(label) <= 10
            separator = "" if one_line else "\n"
            text = f"{label}{separator}({100*fraction:.1f}%)"
            text_radius = radius * (0.65 if crowded else 0.55)
            if crowded:
                # 密集分类把两行文字放在靠外的位置，按文字内侧的扇区宽度约束，
                # 而不是仅按中心点宽度约束，避免标签在圆心附近互相覆盖。
                max_width = radius * 0.6 * radius_px
                max_height = 2 * radius * 0.35 * math.tan(
                    math.radians(min(end-begin, 120))/2
                ) * radius_px * 0.9
            else:
                max_width = radius * 0.9 * radius_px
                max_height = 2 * text_radius * math.sin(math.radians(min(end-begin, 180))/2) * radius_px
            size = fit_text(fig, text, 16, max_width, max_height, family, bold=True)
            if len(active) == 1:
                x, y, rotation = 0, 0, 0
            else:
                x, y = text_radius*math.cos(theta), text_radius*math.sin(theta)
                rotation = mid+(180 if 90 < mid < 270 else 0)
            ax.text(x, y, text, fontsize=size, fontweight="bold", linespacing=1.05,
                    ha="center", va="center", rotation=rotation, rotation_mode="anchor")
        return fig, ax


def draw_categorized_pie(json_path: str | Path = DEFAULT_JSON) -> Path:
    """读取一个 JSON，在项目 results 中生成 PNG、SVG、PDF，返回 PNG 路径。"""
    fig, _ = plot_categorized_pie(json_path)
    try:
        return save_chart(fig, json_path)
    finally:
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json", nargs="?", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    try:
        print(draw_categorized_pie(args.json))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"无法绘制分类饼图：{exc}\n")


if __name__ == "__main__":
    main()
