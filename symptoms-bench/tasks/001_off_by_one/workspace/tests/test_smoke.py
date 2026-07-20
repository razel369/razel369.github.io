import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sum_window import sum_all

def test_sum_includes_last():
    assert sum_all([1, 2, 3, 4]) == 10
