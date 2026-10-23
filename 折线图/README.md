# 折线图

在本目录运行 `python 折线图.py`，输出到当前工作目录下的 `figures/comparison_posttraining.png`。

修改 data_posttraining：

- methods：方法名称。
- colors：每条曲线的颜色。
- steps：横轴标签。
- results：每行对应一个方法，每列对应一个 step。

方法数量、颜色数量与结果行数应一致，每行结果长度应与 steps 一致。原脚本按等间距展示 steps，横轴坐标不是实际数值间距。

保留原脚本及 Helvetica 字体设置；系统未安装时 Matplotlib 会回退到可用字体。默认数值为随附示例，使用时请替换或核实来源。
