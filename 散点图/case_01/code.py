"""Case 01 reproduction. Data inputs live in render_all.py:case01()."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from render_all import case01
case01()
