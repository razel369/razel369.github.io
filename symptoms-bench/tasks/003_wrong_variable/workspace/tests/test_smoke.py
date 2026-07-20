import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clamp import clamp

def test_clamp_low():
    assert clamp(-5, 0, 10) == 0
