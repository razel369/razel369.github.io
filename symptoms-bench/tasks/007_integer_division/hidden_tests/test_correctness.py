import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from stats import mean

def test_mean():
    assert abs(mean([1, 2]) - 1.5) < 1e-9

def test_ints():
    assert mean([2, 2, 2]) == 2
