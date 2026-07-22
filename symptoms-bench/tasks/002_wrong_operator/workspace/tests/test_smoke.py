import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pricing import apply_discount

def test_discount():
    assert abs(apply_discount(100.0, 0.2) - 80.0) < 1e-9
