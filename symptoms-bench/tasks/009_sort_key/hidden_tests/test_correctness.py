import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from rank import longest_first

def test_order():
    assert longest_first(["a", "bbbb", "cc"]) == ["bbbb", "cc", "a"]
