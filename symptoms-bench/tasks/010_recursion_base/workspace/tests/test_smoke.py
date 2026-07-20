import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fact import factorial

def test_fact0():
    assert factorial(0) == 1
