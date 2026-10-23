# draw_picture_repository

六类 Python 科研绘图代码合集，按图表类型整理，保留配套数据、说明及示例效果图。

## 六类目录

| 类型 | 入口 | 自定义数据 |
| --- | --- | --- |
| [柱状图](柱状图/) | reproduce_bar_chart.py | MODELS 中的 values、errors、color |
| [折线图](折线图/) | 折线图.py | data_posttraining 中的 steps、results、methods、colors |
| [散点图](散点图/) | render_all.py 或 case_01/code.py 至 case_16/code.py | render_all.py 中的 caseXX() 函数 |
| [饼图](饼图/) | main.py | categories.json、percentages.json |
| [热力图](热力图/) | reproduce_heatmap.py | --matrix 传入 NPY，或 --input 传入 NPZ |
| [箱式图](箱式图/) | run_all.py 或四个编号脚本 | 各脚本数据区及 life-expectancy-table.json |

## 安装和运行

建议 Python 3.10 或以上。在仓库根目录安装绘图依赖：

```bash
python -m pip install -r requirements.txt
```

下面每组命令均从仓库根目录开始，任选一类执行：

```bash
cd 柱状图
python reproduce_bar_chart.py
```

```bash
cd 折线图
python 折线图.py
```

```bash
cd 散点图
python render_all.py
# 也可只绘制某个示例：python case_01/code.py
```

```bash
cd 饼图
python main.py
```

```bash
cd 热力图
python reproduce_heatmap.py --outdir outputs
```

```bash
cd 箱式图
python run_all.py
```

## 数据与字体

- 柱状图默认数值及误差来自截图估读；颜色按截图取样，字体近似匹配，每根柱子均可单独修改。
- 散点图与热力图包含模拟数据，不代表原论文实验结果。箱式图的数据说明见其目录内 README。
- 保留原有绘图样式。折线图使用 Helvetica，系统未安装时会回退到可用字体。
- 现有 PNG/PDF/SVG 是随源文件提供或此前生成的示例，并非本次全部重新运行生成。
- 箱式图已附带 JSON 缓存；缺少缓存时，第一个示例可能联网下载数据。

## 整理与验证

- 四个压缩包已解压；饼图、热力图去掉多余外层包装目录。
- 保留代码、数据、效果图和说明，排除 Python 缓存、日志、临时检查图片。
- 全部 32 个 Python 文件通过语法解析检查。
- 柱状图已运行验证并生成 PNG/PDF/SVG；其余示例本次未完整执行，整理环境缺少 SciPy。
- 散点图 build_delivery.py 为旧版报告打包工具，需要未提供的索引文件及路径调整，详见该目录说明。
