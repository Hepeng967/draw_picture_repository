# -*- coding: utf-8 -*-
"""
ECharts: data-transform-aggregate（简单的数据聚合）→ Matplotlib
原图：https://echarts.apache.org/examples/zh/editor.html?c=data-transform-aggregate

运行：
    python 01_data_transform_aggregate.py          # 下载原始 ECharts 数据并绘图
    python 01_data_transform_aggregate.py --sample # 使用明确标注的合成数据，离线测试

注意：原图的箱线须为每个国家 Income 的实际 min/max，不是 1.5*IQR。
"""
from pathlib import Path
import argparse
import json
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
DATA_PATH = ROOT / "life-expectancy-table.json"
DATA_URLS = [
    "https://echarts.apache.org/examples/data/asset/data/life-expectancy-table.json",
    "https://raw.githubusercontent.com/apache/echarts-website/master/examples/data/asset/data/life-expectancy-table.json",
]
SHOW_ALL_YEARS = False   # 原版在每个红点标 Year；改 True 可模仿，但全量图较拥挤
VISIBLE_COUNTRIES = None  # None 显示全部；也可设 5，模拟 ECharts dataZoom 的局部视图

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


def load_echarts_data() -> pd.DataFrame:
    """优先使用脚本同目录的原始数据；若不存在则下载并缓存。"""
    if DATA_PATH.exists():
        obj = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    else:
        obj = None
        for url in DATA_URLS:
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(req, timeout=25) as res:
                    obj = json.loads(res.read().decode("utf-8"))
                DATA_PATH.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
                print(f"已下载原始数据：{url}")
                break
            except Exception as exc:
                print(f"尝试数据源失败：{url} ({exc})")
        if obj is None:
            raise RuntimeError(
                "原始数据下载失败。请访问上述 ECharts 数据源，下载 JSON 到脚本同目录，"
                "文件名为 life-expectancy-table.json；或者执行 --sample 离线预览。"
            )

    # ECharts 原始数据格式：第一行为 ['Income', ..., 'Country', 'Year']
    if isinstance(obj, list) and obj and isinstance(obj[0], list) and "Income" in obj[0]:
        df = pd.DataFrame(obj[1:], columns=obj[0])
    elif isinstance(obj, list) and obj and isinstance(obj[0], dict):
        df = pd.DataFrame(obj)
    else:
        raise ValueError("未知数据格式，预期为 ECharts 的 life-expectancy-table.json。")
    return prepare(df)


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("Income", "Year"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.loc[df["Year"].ge(1950), ["Income", "Country", "Year"]].dropna().copy()


def sample_data() -> pd.DataFrame:
    """仅用于离线验证绘图。此数据是合成的，不是 ECharts 原始收入数据。"""
    rng = np.random.default_rng(2026)
    countries = ["Australia", "Canada", "China", "France", "Germany", "India",
                 "Japan", "New Zealand", "Norway", "South Korea", "United Kingdom", "United States"]
    rows = []
    for i, country in enumerate(countries):
        for year in range(1950, 2016, 5):
            income = (1800 + i * 1300) * (1 + (year - 1950) / 80) + rng.normal(0, 500)
            rows.append([max(50, income), country, year])
    return pd.DataFrame(rows, columns=["Income", "Country", "Year"])


def plot(df: pd.DataFrame, is_sample: bool = False):
    # 与 JS 一致：按 Country 聚合，并按 Q3 升序排序。
    groups = df.groupby("Country")["Income"]
    agg = groups.agg(min="min", max="max")
    agg["Q1"] = groups.quantile(0.25)
    agg["median"] = groups.quantile(0.50)
    agg["Q3"] = groups.quantile(0.75)
    agg = agg.sort_values("Q3", kind="stable")
    if VISIBLE_COUNTRIES is not None:
        agg = agg.tail(VISIBLE_COUNTRIES)
    names = list(agg.index)

    # Matplotlib bxp 使用五数概括绘制：显式设置 whisker=min/max。
    stats = [
        {"label": country, "whislo": float(row["min"]), "q1": float(row["Q1"]),
         "med": float(row["median"]), "q3": float(row["Q3"]),
         "whishi": float(row["max"]), "fliers": []}
        for country, row in agg.iterrows()
    ]

    fig, ax = plt.subplots(figsize=(13, max(6.0, len(names) * 0.47 + 1.6)))
    y = np.arange(1, len(names) + 1)
    ax.bxp(stats, positions=y, vert=False, patch_artist=True, widths=0.55,
           showfliers=False, manage_ticks=False,
           boxprops={"facecolor": LIGHT_FILL, "edgecolor": LIGHT_LINE, "linewidth": 1.2},
           whiskerprops={"color": LIGHT_LINE, "linewidth": 1.2},
           capprops={"color": LIGHT_LINE, "linewidth": 1.2},
           medianprops={"color": LIGHT_MEDIAN, "linewidth": 1.7})

    # 与 ECharts 第二个 scatter series 对应：画每个年份的原始收入观测。
    for yi, country in zip(y, names):
        part = df.loc[df["Country"].eq(country), ["Income", "Year"]]
        # 注意：这里画的是全部年度原始数据点，并非按 1.5×IQR 判断的离群点。
        # 为保持全套风格一致，原始数据点也采用浅青色空心圆。
        ax.scatter(part["Income"], np.full(len(part), yi), s=20,
                   facecolors="none", edgecolors=OUTLIER_LINE,
                   linewidths=1.05, alpha=0.88, zorder=3)
        if SHOW_ALL_YEARS:
            for income, year in part.itertuples(index=False, name=None):
                ax.annotate(str(int(year)), (income, yi), xytext=(0, 5),
                            textcoords="offset points", rotation=90,
                            fontsize=6.3, fontweight="bold", ha="left", color=OUTLIER_LINE)

    ax.set_yticks(y, names)
    ax.set_ylim(0.5, len(names) + 0.5)
    ax.set_xlabel("Income", labelpad=12, fontweight="bold")
    ax.set_title("Income since 1950" + ("  [SYNTHETIC PREVIEW]" if is_sample else ""), pad=18, fontweight="bold")
    ax.grid(axis="x", color="#e9edf3")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight("bold")
    fig.tight_layout()
    stem = "01_data_transform_aggregate_sample" if is_sample else "01_data_transform_aggregate"
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
    print(f"完成：{OUT / (stem + '.png')}（{len(names)} 个国家）")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="无需网络，使用标明为合成的测试数据")
    args = parser.parse_args()
    plot(sample_data() if args.sample else load_echarts_data(), is_sample=args.sample)
