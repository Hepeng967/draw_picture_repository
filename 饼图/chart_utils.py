"""共用数据校验与排版工具；两类图的配色各自维护。"""

from __future__ import annotations

import json
import math
from pathlib import Path

from matplotlib import font_manager
from matplotlib.font_manager import FontProperties


def load_records(json_path: str | Path) -> list[dict]:
    path = Path(json_path)
    if path.suffix.lower() != ".json":
        raise ValueError("输入文件扩展名必须为 .json。")
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.name} 第 {exc.lineno} 行不是有效 JSON：{exc.msg}") from exc
    if not isinstance(data, list) or not data:
        raise ValueError(f"{path.name} 的顶层必须是非空数组。")
    for i, record in enumerate(data):
        if not isinstance(record, dict):
            raise ValueError(f"第 {i + 1} 项必须是包含 name、value 的对象。")
    return data


def number(value: object, location: str) -> float:
    if value is None:
        return 1.0
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{location} 必须为非负数或 null。")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{location} 数值过大。") from exc
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{location} 必须为有限非负数。")
    return result


def name(value: object, fallback: str) -> str:
    if value is None or value == "":
        return fallback
    if not isinstance(value, str):
        raise ValueError(f"{fallback} 的 name 必须为字符串。")
    return value


def shares(values: list[float], location: str = "value") -> list[float]:
    maximum = max(values, default=0)
    if maximum <= 0:
        raise ValueError(f"{location} 至少需要一个正数。")
    # 先缩放再求和，允许大数值输入，不依赖总和等于 100。
    scaled = [value / maximum for value in values]
    total = math.fsum(scaled)
    return [value / total for value in scaled]


def fonts(serif: bool = False) -> list[str]:
    available = {font.name for font in font_manager.fontManager.ttflist}
    fallback = next((f for f in (
        "Microsoft YaHei", "SimHei", "Noto Sans CJK SC",
        "WenQuanYi Micro Hei", "Arial Unicode MS",
    ) if f in available), None)
    return ["DejaVu Serif" if serif else "DejaVu Sans"] + ([fallback] if fallback else [])


def text_size(fig, text: str, size: float, family: list[str],
              bold: bool = False) -> tuple[float, float]:
    renderer = fig.canvas.get_renderer()
    prop = FontProperties(family=family, size=size, weight="bold" if bold else "normal")
    lines = text.splitlines() or [""]
    measured_width = max(renderer.get_text_width_height_descent(line, prop, False)[0] for line in lines)
    measured_height = size * fig.dpi / 72 * len(lines) * 1.1
    return measured_width, measured_height


def fit_text(fig, text: str, size: float, width: float, height: float,
             family: list[str], bold: bool = False) -> float:
    """按未旋转文字的实际宽高缩小字号，width/height 均为像素。"""
    measured_width, measured_height = text_size(fig, text, size, family, bold)
    scale = min(1, width / max(1, measured_width), height / max(1, measured_height))
    return max(0.1, size * scale)


def save_chart(fig, json_path: str | Path) -> Path:
    """在项目 results 目录生成 PNG、SVG、PDF，返回 PNG 路径。"""
    results = Path(__file__).resolve().parent / "results"
    results.mkdir(parents=True, exist_ok=True)
    stem = Path(json_path).stem
    for extension in (".png", ".svg", ".pdf"):
        fig.savefig(
            results / f"{stem}{extension}",
            facecolor="white", bbox_inches="tight", pad_inches=0.15,
        )
    return results / f"{stem}.png"
