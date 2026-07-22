import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from find import find_first

def test_find():
    assert find_first([9, 8, 7], 7) == 2
