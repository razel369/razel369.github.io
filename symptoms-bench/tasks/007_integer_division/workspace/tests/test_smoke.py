import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stats import mean

def test_half():
    assert abs(mean([1, 2]) - 1.5) < 1e-9
