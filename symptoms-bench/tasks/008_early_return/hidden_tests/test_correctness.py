import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from find import find_first

def test_later():
    assert find_first([9, 8, 7], 7) == 2

def test_missing():
    assert find_first([1, 2], 5) is None

def test_first():
    assert find_first([3, 1], 3) == 0
