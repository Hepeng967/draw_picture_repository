# JSON 驱动的两种饼图

只需修改两个 JSON，再运行主文件。无需设置颜色、分类数量、比例、字体、画布大小等绘图参数。

## 运行

需要 Python 3.10+：

```sh
python -m pip install -r requirement.txt
python main.py
```

主文件默认读取**代码所在目录**的：

- `categories.json` → 分类饼图 `results/categories.png`、`results/categories.svg`、`results/categories.pdf`
- `percentages.json` → 百分比饼图 `results/percentages.png`、`results/percentages.svg`、`results/percentages.pdf`

默认 JSON 已填入参考图的示例数据。日常使用只需编辑它们，再运行 `python main.py`；输出文件会更新。SVG、PDF 可无损放大。

也可以提供其他 JSON 路径，参数顺序为分类图、百分比图：

```sh
python main.py my_categories.json my_percentages.json
```

只绘制其中一张：

```sh
python categorized_pie.py categories.json
python percentage_pie.py percentages.json
```

输出统一放在代码所在目录的 `results` 文件夹，程序会自动创建该文件夹，不向 JSON 所在目录或当前运行目录写入图片。结果沿用输入 JSON 的文件名，扩展名分别为 `.png`、`.svg`、`.pdf`。例如 `my_categories.json` 会生成 `results/my_categories.png` 等三个文件；同名结果会在下次运行时更新。

## 百分比饼图 JSON

顶层是数组，每项把名称和数值放在一起：

```json
[
  {"name": "功能错误", "value": 50},
  {"name": "名称错误", "value": 30},
  {"name": "类型错误", "value": 20}
]
```

- `name`：名称。
- `value`：数量、权重或比例；无需加百分号，不要求总和等于 100。
- 占比 = 当前 `value` / 所有 `value` 之和，扇区角度与标签来自同一组数值。
- `[50, 30, 20]`、`[5, 3, 2]` 和 `[0.5, 0.3, 0.2]` 的扇区大小相同。
- 添加或删除对象即可改变选项数量。

风格：柔和配色、分离扇区、白色分隔、灰色粗体百分比、右侧带边框的图例，英文采用衬线字体。参考数据中最小的 2% 扇区不标注百分比，保持与参考图一致；选项增多时自动调整标注阈值、字号和画布。百分比为整数时显示整数，否则自动显示一位小数。

## 分类饼图 JSON

顶层也是数组，每个分类包含 `name`、`value` 和 `children`：

```json
[
  {
    "name": "开发",
    "value": 40,
    "children": ["编辑器", "调试工具"]
  },
  {
    "name": "办公",
    "value": 60,
    "children": ["文档", "表格", "演示"]
  }
]
```

- 分类 `value` 决定内层分类占比；本例分别为 40%、60%。
- `children` 决定所属分类的外层项目。名称列表默认均分父分类。
- 本例开发的两个子项各占整图 20%，办公的三个子项也各占整图 20%。
- **增删子项只改变所属分类内部的划分，不改变父分类占比。**
- 分类数量与每类子项数量都可以自由变化，不需要填写数量参数。

如果子项大小不同，把子项名称改成包含相对权重的对象：

```json
[
  {
    "name": "开发",
    "value": 40,
    "children": [
      {"name": "编辑器", "value": 3},
      {"name": "调试工具", "value": 1}
    ]
  },
  {
    "name": "办公",
    "value": 60,
    "children": ["文档", "表格", "演示"]
  }
]
```

开发仍占整图 40%，其两个子项按 3:1 分配，分别占整图 30%、10%。子项 `value` 是**类内权重**，不用与父分类 `value` 相加对应。

风格：内层实心分类饼图、外层同色系渐变环、白色分隔线、径向文字和粗体分类占比。父子扇区共用角度边界。程序会按数量和文字长度自动调整画布、字号。极端密集或极小的扇区可能需要通过 SVG 放大查看。

## 独立色彩库

- `categorized_colors.py`：分类图色彩库。保留参考图六种分类色及各自的外层渐变色阶。
- `percentage_colors.py`：百分比图色彩库。保留参考图七种柔和颜色。

两套配色互不依赖，按 JSON 中的顺序自动选取。超过参考数量时，先使用扩展色库，再生成同风格、与已有颜色尽量区分的新颜色，不简单循环前几种颜色。颜色跟随输入顺序；调整顺序会改变对应颜色。JSON 中不需要也不接受样式参数。

## 默认与数据校验

- `value` 省略或为 `null` 时，用 1 作为默认权重；相应百分比也基于 1 计算，不显示与图形分离的占位百分比。
- 名称省略、为空或为 `null` 时，自动使用 `Item 01`、`Category 1` 等占位名称。
- 分类的 `children` 省略或为 `null` 时，生成一个默认子项。
- 零值扇区不绘制；普通饼图的零值选项保留在图例中。
- 不接受负值、字符串数值、布尔值、非有限数值、空顶层数组、空子项数组或总权重为零的数据。正值分类的子项权重也不能全部为零。
- 为避免把字段拼写错误当成默认值，未知字段会明确报错。
- 数值缺失时只是演示权重；真实统计请填写真实数值。
- 不接受旧版 `items/label`、`labels/values` 格式；已统一为上述 `name/value/children` 结构，旧版绘图超参数入口已移除。

## 在其他 Python 程序中调用

入口仍然只有 JSON 路径：

```python
from categorized_pie import draw_categorized_pie
from percentage_pie import draw_percentage_pie

draw_categorized_pie("categories.json")
draw_percentage_pie("percentages.json")
```

两个函数自动将 PNG、SVG、PDF 保存到项目的 `results` 文件夹，并返回 PNG 的绝对路径。若只需要 Matplotlib 图形对象，可调用对应的 `plot_categorized_pie(json_path)` 或 `plot_percentage_pie(json_path)`，返回 `(fig, ax)`，由调用方关闭图形。

中文优先使用系统中的微软雅黑、黑体或 Noto Sans CJK SC；非 Windows 系统请确保已安装中文字体。

