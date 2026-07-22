import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from filter_words import contains_banned

def test_banned_casefold():
    assert contains_banned("Hello WORLD", ["world"]) is True
