import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from pricing import apply_discount

def test_twenty_percent():
    assert abs(apply_discount(100.0, 0.2) - 80.0) < 1e-9

def test_zero():
    assert apply_discount(50.0, 0.0) == 50.0

def test_full():
    assert apply_discount(40.0, 1.0) == 0.0
