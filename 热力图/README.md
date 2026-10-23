# Figure 7 热力图样式复现

参考：Ying, Zhao, Yu. **Boosting Graph Pooling with Persistent Homology**, NeurIPS 2024, Figure 7（PDF 第 17 页）。

https://proceedings.neurips.cc/paper_files/paper/2024/file/21f76686538a5f06dc431efea5f475f5-Paper-Conference.pdf#page=17

## 数据声明

这是**可视化样式的近似复现**，不是论文实验结果复现。
默认六个矩阵是由脚本生成的模拟数据，局部模式参照原图；并非作者的原始邻接矩阵，也不是从图片反推出的精确数值。
渐变色控制点由原图的外观近似配置，没有声称使用作者原始色板。
默认图片标注 `Synthetic example`，合成大图也包含模拟数据说明。

## 环境与运行

建议 Python 3.10 或以上。

```bash
pip install -r requirements.txt
python reproduce_heatmap.py --outdir heatmap_outputs
```

默认使用固定随机种子 42。生成六个独立热图的 PNG/PDF/SVG，再将它们排列成三行两列的 PNG 与矢量 PDF。
不需要训练模型，不需要 GPU，也不依赖 Seaborn。

## 换成自己的一个矩阵

先准备一个方阵 `adjacency.npy`，例如由模型导出：

```python
# 已有 PyTorch Tensor 时：
np.save("adjacency.npy", adjacency.detach().cpu().numpy())
# 已有 NumPy 数组时：
np.save("adjacency.npy", adjacency)
```

然后运行：

```bash
python reproduce_heatmap.py --matrix adjacency.npy --title "My adjacency matrix" --outdir my_plot --dpi 600
```

生成 `my_plot/heatmap_single.png`、`.pdf`、`.svg`。
用户提供的数据不会添加模拟数据说明。

也可以作为函数导入：

```python
import numpy as np
from reproduce_heatmap import draw_heatmap

A = np.load("adjacency.npy", allow_pickle=False)
draw_heatmap(A, "My adjacency matrix", "my_plot/heatmap", dpi=600)
```

## 换成自己的六个矩阵

每个矩阵须为有限实数方阵，不要求六个矩阵尺寸相同。下列变量应替换为自己的实验矩阵。

```python
np.savez(
    "matrices.npz",
    diffpool_l1=A1, diffpool_l2=A2,
    mincut_l1=A3, mincut_l2=A4,
    dmon_l1=A5, dmon_l2=A6,
)
```

```bash
python reproduce_heatmap.py --input matrices.npz --outdir real_outputs
```

更改脚本中的 `LABELS` 可以替换方法名称。键名 `KEYS` 应与 NPZ 文件保持一致。

## 配色与刻度

`PALETTE`：浅青绿—蓝—紫的渐变控制点。
`--linewidth`：白色格子分隔线的宽度，默认 0.85 pt。
`--dpi`：PNG 输出分辨率，默认 300；PDF 和 SVG 的矩阵与色条为矢量对象。
`--vmin` / `--vmax`：色条上下限，仅控制颜色映射，不修改矩阵数值。

默认模拟图使用接近参考图的独立色条范围。因此，不同图里同样深的紫色不一定对应相同数值。
使用真实数据比较不同方法的绝对数值时，可显式指定相同色条上下限：

```bash
python reproduce_heatmap.py --input matrices.npz --vmin 0 --vmax 1 --outdir shared_scale
```

只有在数据确实适合此范围时才使用 0 到 1；否则选择数据的实际范围。范围之外的值会被显示成端点颜色。
不指定上下限时，用户数据按各自最小值和最大值映射颜色。
脚本不会对用户矩阵归一化、排序或对称化。

## 已生成文件

- `outputs/heatmap_figure7_style.png`：300 dpi 完整热图。
- `outputs/heatmap_figure7_style.pdf`：完整矢量热图。
- `outputs/heatmap_preview.png`：缩小预览。
- `outputs/panels/`：六个热图各自的 PNG/PDF/SVG。
- `outputs/synthetic_demo_matrices.npz`：本次示例数据，全部为模拟数据。
- `reproduce_heatmap.py`：完整绘图脚本。
