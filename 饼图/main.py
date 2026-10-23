"""运行 python main.py，默认读取两个 JSON 并绘制两张图，无需设置绘图参数。"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from categorized_pie import DEFAULT_JSON as CATEGORIES_JSON, draw_categorized_pie
from percentage_pie import DEFAULT_JSON as PERCENTAGES_JSON, draw_percentage_pie


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("categories_json", nargs="?", type=Path, default=CATEGORIES_JSON)
    parser.add_argument("percentages_json", nargs="?", type=Path, default=PERCENTAGES_JSON)
    args = parser.parse_args()
    try:
        for draw, path in (
            (draw_categorized_pie, args.categories_json),
            (draw_percentage_pie, args.percentages_json),
        ):
            png = draw(path)
            print(f"已生成：{png}")
            print(f"已生成：{png.with_suffix('.svg')}")
            print(f"已生成：{png.with_suffix('.pdf')}")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"绘图失败：{exc}\n")


if __name__ == "__main__":
    main()
