import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rank import longest_first

def test_long_first():
    assert longest_first(["a", "bbbb", "cc"]) == ["bbbb", "cc", "a"]
