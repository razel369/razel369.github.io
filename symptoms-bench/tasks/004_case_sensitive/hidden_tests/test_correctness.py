import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
from filter_words import contains_banned

def test_case():
    assert contains_banned("Hello WORLD", ["world"]) is True

def test_absent():
    assert contains_banned("hi there", ["bye"]) is False
