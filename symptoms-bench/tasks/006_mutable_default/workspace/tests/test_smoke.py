import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bags import append_item

def test_no_leak():
    a = append_item("x")
    b = append_item("y")
    assert a == ["x"]
    assert b == ["y"]
