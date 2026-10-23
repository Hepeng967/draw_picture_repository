# -*- coding: utf-8 -*-
"""一键运行四个箱线图示例；首次绘制 01 正式版需下载原始 JSON。"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
scripts = [
    "01_data_transform_aggregate.py",
    "02_boxplot_light_velocity.py",
    "03_boxplot_light_velocity2.py",
    "04_boxplot_multi.py",
]
for script in scripts:
    cmd = [sys.executable, str(ROOT / script)]
    if script.startswith('01') and '--sample-first' in sys.argv:
        cmd.append('--sample')
    print('RUN', script, flush=True)
    subprocess.run(cmd, check=True)
