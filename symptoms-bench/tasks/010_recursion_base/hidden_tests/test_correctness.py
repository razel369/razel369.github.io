import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from fact import factorial

def test_zero():
    assert factorial(0) == 1

def test_five():
    assert factorial(5) == 120
