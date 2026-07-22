import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from sum_window import sum_all

def test_basic():
    assert sum_all([1, 2, 3, 4]) == 10

def test_single():
    assert sum_all([7]) == 7

def test_empty():
    assert sum_all([]) == 0
