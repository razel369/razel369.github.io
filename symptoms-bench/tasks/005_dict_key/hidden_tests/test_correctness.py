import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from histogram import count_items

def test_counts():
    assert count_items(["a", "b", "a"]) == {"a": 2, "b": 1}

def test_empty():
    assert count_items([]) == {}
