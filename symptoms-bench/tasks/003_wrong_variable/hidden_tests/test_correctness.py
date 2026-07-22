import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from clamp import clamp

def test_below():
    assert clamp(-5, 0, 10) == 0

def test_above():
    assert clamp(99, 0, 10) == 10

def test_inside():
    assert clamp(3, 0, 10) == 3
