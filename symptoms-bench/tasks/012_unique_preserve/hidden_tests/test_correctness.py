import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from unique import unique_preserve

def test_order():
    assert unique_preserve(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]
