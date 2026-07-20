import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import join_path

def test_sep():
    out = join_path("/tmp/data", "file.txt")
    assert out.replace("\\", "/") == "/tmp/data/file.txt"
