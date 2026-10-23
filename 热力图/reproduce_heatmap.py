#!/usr/bin/env python3
"""Re-create the visual style of Figure 7 in Ying et al., NeurIPS 2024.

IMPORTANT: default matrices are SYNTHETIC. Neither their entries nor the
palette control points are the authors' original numerical data/settings.
The palette and visual patterns were approximated from the published figure.

Dependencies: numpy, matplotlib, pillow, pymupdf
Examples:
    python reproduce_heatmap.py
    python reproduce_heatmap.py --matrix adjacency.npy --title "My adjacency"
    python reproduce_heatmap.py --input matrices.npz --vmin 0 --vmax 1

Reference:
https://proceedings.neurips.cc/paper_files/paper/2024/file/
21f76686538a5f06dc431efea5f475f5-Paper-Conference.pdf#page=17
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FormatStrFormatter
from PIL import Image, ImageDraw, ImageFont
import fitz

# Approximate the specifically requested mint -> blue -> purple palette.
# These are manually selected reference-style colors, not recovered author code.
PALETTE = ["#BFE5D8", "#95CBC5", "#72A8B8", "#637EAB", "#504887", "#321E3D"]
CMAP = LinearSegmentedColormap.from_list("mint_blue_purple", PALETTE, N=256)

KEYS = ("diffpool_l1", "diffpool_l2", "mincut_l1", "mincut_l2", "dmon_l1", "dmon_l2")
LABELS = ("(a) DiffPool-layer-1", "(b) DiffPool-layer-2",
          "(c) MinCutPool-layer-1", "(d) MinCutPool-layer-2",
          "(e) DMoNPool-layer-1", "(f) DMoNPool-layer-2")
DEMO_MAX = (35.5, 62.0, 0.27, 0.53, 0.048, 0.17)
DEMO_TICKS = (np.arange(5, 36, 5), np.arange(10, 61, 10),
              np.arange(0, 0.251, 0.05), np.arange(0, 0.501, 0.1),
              np.arange(0, 0.041, 0.01), np.arange(0, 0.161, 0.02))
DEMO_FORMATS = ("%.0f", "%.0f", "%.2f", "%.1f", "%.2f", "%.2f")
PANEL_SIZE = (4.10, 4.15)  # inches; fixed size preserves alignment in the montage


def validate_matrix(matrix: np.ndarray) -> np.ndarray:
    """Require a finite, nonempty, real-valued square matrix."""
    raw = np.asarray(matrix)
    if np.iscomplexobj(raw):
        raise ValueError("The matrix must contain real values, not complex values.")
    matrix = np.asarray(raw, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.size == 0:
        raise ValueError(f"Expected a nonempty square matrix; received {matrix.shape}.")
    if not np.isfinite(matrix).all():
        raise ValueError("The matrix contains NaN or infinity.")
    return matrix


def make_demo_matrices(seed: int = 42) -> dict[str, np.ndarray]:
    """Synthetic illustrative matrices; NOT published experimental results."""
    rng = np.random.default_rng(seed)
    n = 28

    # Almost uniform light background, with one large diagonal entry.
    strength = rng.uniform(0.13, 0.38, n)
    strength[23] = np.sqrt(35.5)
    diff1 = np.outer(strength, strength)

    # A coarser matrix with a dominant central entry.
    diff2 = np.array([
        [0.8, 0.2, 0.4, 8.2, 0.5, 0.6, 0.4],
        [0.2, 0.5, 0.3, 3.1, 0.4, 0.3, 0.4],
        [0.4, 0.3, 0.6, 1.8, 0.3, 0.4, 0.5],
        [8.2, 3.1, 1.8, 62., 1.5, 2.4, 4.2],
        [0.5, 0.4, 0.3, 1.5, 0.4, 0.4, 0.3],
        [0.6, 0.3, 0.4, 2.4, 0.4, 0.6, 0.4],
        [0.4, 0.4, 0.5, 4.2, 0.3, 0.4, 0.5],
    ])

    # Heterogeneous row/column strengths with symmetric isolated peaks.
    strength = rng.uniform(0.02, 0.11, n)
    strength[[7, 8, 12, 18, 21]] = [0.27, 0.25, 0.22, 0.26, 0.23]
    min1 = np.outer(strength, strength)
    noise = rng.uniform(0.0, 0.017, (n, n))
    min1 += (noise + noise.T) / 2
    for i, j, value in [(7, 8, .27), (7, 12, .23), (8, 18, .19),
                         (8, 21, .17), (12, 18, .16), (18, 21, .18),
                         (7, 24, .13), (8, 24, .12), (18, 24, .10)]:
        min1[i, j] = min1[j, i] = value
    np.fill_diagonal(min1, 0.0)

    min2 = np.array([
        [0., .14, .17, .19, .16, .13, .53],
        [.14, 0., .10, .11, .10, .07, .22],
        [.17, .10, 0., .13, .11, .12, .29],
        [.19, .11, .13, 0., .13, .11, .34],
        [.16, .10, .11, .13, 0., .08, .26],
        [.13, .07, .12, .11, .08, 0., .25],
        [.53, .22, .29, .34, .26, .25, 0.],
    ])

    # A dense matrix with a pale zero diagonal and dark off-diagonal entries.
    noise = rng.normal(0.0, 0.004, (n, n))
    dmon1 = np.clip(0.038 + (noise + noise.T) / 2, 0.024, 0.048)
    np.fill_diagonal(dmon1, 0.0)
    dmon2 = np.full((7, 7), 1.0 / 6.0)
    np.fill_diagonal(dmon2, 0.0)
    return dict(zip(KEYS, (diff1, diff2, min1, min2, dmon1, dmon2)))


def draw_heatmap(
    matrix: np.ndarray,
    label: str,
    output_stem: str | Path,
    *,
    vmin: float | None = None,
    vmax: float | None = None,
    ticks: Sequence[float] | None = None,
    tick_format: str | None = None,
    linewidth: float = 0.85,
    dpi: int = 300,
    note: str | None = None,
) -> Path:
    """Draw ONE heatmap; save its PNG and vector PDF/SVG.

    The input matrix is not modified, normalized, reordered, or symmetrized.
    vmin/vmax change only the color scale. Use common limits for comparable data.
    """
    matrix = validate_matrix(matrix)
    if dpi <= 0 or linewidth < 0:
        raise ValueError("dpi must be positive and linewidth must be nonnegative.")
    lo = float(matrix.min()) if vmin is None else float(vmin)
    hi = float(matrix.max()) if vmax is None else float(vmax)
    if not np.isfinite([lo, hi]).all() or hi < lo:
        raise ValueError("Color limits must be finite and satisfy vmax >= vmin.")
    if hi == lo:
        hi = lo + max(abs(lo) * 0.01, 1e-6)

    stem = Path(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    width, height = PANEL_SIZE
    with plt.rc_context({"font.family": "STIXGeneral", "pdf.fonttype": 42,
                         "svg.fonttype": "none", "axes.unicode_minus": False}):
        fig = plt.figure(figsize=PANEL_SIZE, facecolor="white")
        # Fixed physical coordinates in inches: x, y, width, height.
        ax = fig.add_axes([0.10 / width, 0.61 / height, 3.20 / width, 3.20 / height])
        cax = fig.add_axes([3.48 / width, 0.61 / height, 0.13 / width, 3.20 / height])
        mesh = ax.pcolormesh(
            matrix, cmap=CMAP, vmin=lo, vmax=hi, shading="flat",
            edgecolors="white", linewidth=linewidth, antialiased=True,
            rasterized=False,
        )
        ax.set_aspect("equal")
        ax.set_xlim(0, matrix.shape[1])
        ax.set_ylim(matrix.shape[0], 0)  # matrix [0, 0] at top left
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        cbar = fig.colorbar(mesh, cax=cax, ticks=ticks)
        cbar.outline.set_visible(False)
        cbar.ax.tick_params(labelsize=8.8, length=0, pad=4, colors="#555555")
        if tick_format is not None:
            cbar.ax.yaxis.set_major_formatter(FormatStrFormatter(tick_format))
        if cbar.solids is not None:
            cbar.solids.set_edgecolor("face")  # avoid hairline seams in vector viewers
            cbar.solids.set_rasterized(False)
        fig.text(1.70 / width, 0.32 / height, label,
                 ha="center", va="center", fontsize=17.2)
        if note:
            fig.text(1.70 / width, 0.008, note, ha="center", va="bottom", fontsize=7.5,
                     color="#666666")
        for ext in ("png", "pdf", "svg"):
            fig.savefig(stem.with_suffix("." + ext), dpi=dpi, facecolor="white")
        plt.close(fig)
    return stem


def assemble_panels(stems: Sequence[Path], output_dir: Path, dpi: int,
                    note: str = "") -> Path:
    """Compose six separately rendered charts into a 3-by-2 PNG/vector PDF.

    Charts are independent figures; Pillow/PyMuPDF only arrange their outputs.
    """
    if len(stems) != 6:
        raise ValueError("The montage requires exactly six panels.")
    gap_x, gap_y, footer = 0.12, 0.04, (0.26 if note else 0.0)
    w, h = PANEL_SIZE
    total_w = 2 * w + gap_x
    total_h = 3 * h + 2 * gap_y + footer
    canvas = Image.new("RGB", (round(total_w * dpi), round(total_h * dpi)), "white")
    pdf = fitz.open()
    page = pdf.new_page(width=total_w * 72, height=total_h * 72)
    for k, stem in enumerate(stems):
        row, col = divmod(k, 2)
        x, y = col * (w + gap_x), row * (h + gap_y)
        with Image.open(stem.with_suffix(".png")) as panel:
            canvas.paste(panel.convert("RGB"), (round(x * dpi), round(y * dpi)))
        with fitz.open(stem.with_suffix(".pdf")) as source:
            rect = fitz.Rect(x * 72, y * 72, (x + w) * 72, (y + h) * 72)
            page.show_pdf_page(rect, source, 0)
    if note:
        font_path = font_manager.findfont("STIXGeneral")
        font = ImageFont.truetype(font_path, size=round(8.0 * dpi / 72))
        ImageDraw.Draw(canvas).text(
            (canvas.width / 2, (total_h - footer / 2) * dpi), note,
            font=font, anchor="mm", fill="#666666",
        )
        box = fitz.Rect(0, (total_h - footer) * 72, total_w * 72, total_h * 72)
        page.insert_textbox(box, note, fontname="tiro", fontsize=8.0,
                            align=1, color=(0.4, 0.4, 0.4))
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / "heatmap_figure7_style.png"
    canvas.save(png_path, dpi=(dpi, dpi))
    pdf.set_metadata({"title": "Figure 7 visual-style reproduction",
                      "subject": note or "User-provided matrices"})
    pdf.save(output_dir / "heatmap_figure7_style.pdf", deflate=True, garbage=4)
    pdf.close()
    # Lightweight display preview; the full-resolution PNG is retained above.
    canvas.thumbnail((1250, 1900), Image.Resampling.LANCZOS)
    canvas.save(output_dir / "heatmap_preview.png")
    return png_path


def main(argv: Sequence[str] | None = None) -> Path:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--input", type=Path, help="NPZ with the six keys in KEYS")
    group.add_argument("--matrix", type=Path, help="A single square NPY matrix")
    parser.add_argument("--title", default="Adjacency matrix")
    parser.add_argument("--outdir", type=Path, default=Path("heatmap_outputs"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--linewidth", type=float, default=0.85)
    parser.add_argument("--vmin", type=float, default=None)
    parser.add_argument("--vmax", type=float, default=None)
    args = parser.parse_args(argv)
    if args.dpi < 72:
        parser.error("--dpi must be at least 72.")
    if args.matrix:
        matrix = np.load(args.matrix, allow_pickle=False)
        stem = draw_heatmap(matrix, args.title, args.outdir / "heatmap_single",
                            vmin=args.vmin, vmax=args.vmax, dpi=args.dpi,
                            linewidth=args.linewidth)
        print(f"Saved single-matrix PNG/PDF/SVG to {args.outdir.resolve()}")
        return stem.with_suffix(".png")

    synthetic = args.input is None
    if synthetic:
        matrices = make_demo_matrices(args.seed)
    else:
        with np.load(args.input, allow_pickle=False) as archive:
            missing = set(KEYS) - set(archive.files)
            if missing:
                raise ValueError(f"NPZ missing keys: {sorted(missing)}")
            matrices = {key: validate_matrix(archive[key]) for key in KEYS}
    args.outdir.mkdir(parents=True, exist_ok=True)
    if synthetic:
        np.savez_compressed(args.outdir / "synthetic_demo_matrices.npz", **matrices)
    stems = []
    for i, (key, label) in enumerate(zip(KEYS, LABELS)):
        use_demo_scale = synthetic and args.vmin is None and args.vmax is None
        stem = draw_heatmap(
            matrices[key], label, args.outdir / "panels" / key,
            vmin=0.0 if use_demo_scale else args.vmin,
            vmax=DEMO_MAX[i] if use_demo_scale else args.vmax,
            ticks=DEMO_TICKS[i] if use_demo_scale else None,
            tick_format=DEMO_FORMATS[i] if use_demo_scale else None,
            linewidth=args.linewidth, dpi=args.dpi,
            note="Synthetic example" if synthetic else None,
        )
        stems.append(stem)
    note = ("Synthetic matrices - visual-style reproduction, not the paper's experimental data."
            if synthetic else "")
    result = assemble_panels(stems, args.outdir, args.dpi, note)
    print(f"Saved 6 panels and the combined PNG/PDF to {args.outdir.resolve()}")
    return result


if __name__ == "__main__":
    main()
