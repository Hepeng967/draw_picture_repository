# 四个 Apache ECharts 箱线图的 Python 复刻版

这套代码**只使用 Python + Matplotlib / Pandas / NumPy，不需要 JavaScript**。每个 `.py` 文件可以独立运行，自动保存图片到 `output/`；每张图同时输出 PNG（300 dpi）、PDF（矢量）和 SVG（矢量）。

## 环境配置

```bash
pip install -r requirements.txt
```

## 四个示例

| 文件 | ECharts 原始示例 | Python 输出 | 原始数据处理 |
| --- | --- | --- | --- |
| `01_data_transform_aggregate.py` | [简单的数据聚合](https://echarts.apache.org/examples/zh/editor.html?c=data-transform-aggregate) | 横向箱线图 + 原始年度散点 | 读取官方 `life-expectancy-table.json`、筛选 Year≥1950、按 Country 分组、按 Q3 排序；箱线须是最小值/最大值 |
| `02_boxplot_light_velocity.py` | [基础盒须图](https://echarts.apache.org/examples/zh/editor.html?c=boxplot-light-velocity) | 纵向箱线图 + 离群点 | 与 ECharts 源码完全相同的 5 组实测数据，采用 1.5×IQR 的须线 |
| `03_boxplot_light_velocity2.py` | [垂直方向盒须图](https://echarts.apache.org/examples/zh/editor.html?c=boxplot-light-velocity2) | 横向箱线图 + 离群点 | 使用第 2 个示例的相同数据与统计规则，仅改变方向 |
| `04_boxplot_multi.py` | [多系列盒须图](https://echarts.apache.org/examples/zh/editor.html?c=boxplot-multi) | 三个系列 × 18 类分组箱线图 | 每类每组从 [0,200) 生成 100 个值；固定随机种子，便于复现；分别输出全图和约 20% 的局部图 |

运行：

```bash
python 01_data_transform_aggregate.py
python 02_boxplot_light_velocity.py
python 03_boxplot_light_velocity2.py
python 04_boxplot_multi.py
```

**关于第一幅图的数据：** ECharts 官方示例依赖额外的 JSON 数据源，因此首次执行需要联网下载，随后会缓存成同目录的 `life-expectancy-table.json`；也可以自己提前从 https://echarts.apache.org/examples/data/asset/data/life-expectancy-table.json 下载到此文件夹。没有网络、只想测试绘图，可以运行 `python 01_data_transform_aggregate.py --sample`，它使用明确标注为 **SYNTHETIC PREVIEW** 的合成测试数据（不是 ECharts 原始数据）。

## 与 JS 原版的区别

- 用 Matplotlib 输出静态出版级图表。ECharts 的鼠标悬停 tooltip、浏览器拖动缩放滑块等交互**不会保留**。第 1 图通过 `VISIBLE_COUNTRIES` 选择展示国家数量，第 4 图额外保存前 4 类的局部图，代替网页的缩放默认视图。
- 第 1 图的 `SHOW_ALL_YEARS = False` 默认关闭逐点年份标记，避免大量标签重叠；改为 `True` 即可按照 ECharts 源码绘制年份文字。
- 第 4 图使用固定随机种子以便结果复现，因此具体箱体位置不可能与每次刷新都会重新随机生成的 JS 原图数值完全一致；数据生成过程和图形结构相同。
- 箱线图的须线与离群点遵循 Matplotlib `whis=1.5`（位于 1.5×IQR 范围内的最远观测值为须端），而第 1 图因原版另有约定，直接使用聚合 min/max。

## 如果用于论文

一般建议论文插图用 `output/*.pdf` 或 `*.svg`，需要位图时使用 `*.png`。颜色、标题、字号、输出宽高都在各脚本的 `draw()`/`plot()` 中修改。

也可直接一键运行全部：

```bash
python run_all.py                 # 01 首次会访问官方数据源
python run_all.py --sample-first  # 全部离线测试，01 使用合成数据预览
```

## 颜色、空心离群点与字体（最新版本）

- 箱体主填充色：`#67E8F9`（RGB 103, 232, 249）。
- 箱体边框、须线和帽线：`#78C5D1`（柔和浅青色）；中位数线：`#4AA7B7`。
- 离群点使用**空心圆**：`markerfacecolor="none"`，圆圈边框 `#75B9C5`。
- 图 1 的散点是**全部原始观测值**，不是统计意义上的离群点；为统一视觉风格，也改成了空心圆。
- 字体运行时自动检查：如果系统安装 `Times New Roman`，使用 **Times New Roman Bold**；否则明确选择 **DejaVu Sans Bold**，不会反复触发 Times New Roman 未安装的字体告警。
- 图 4 的三个箱体系列保留三种略有差异的浅青色填充，避免完全无法区分。
