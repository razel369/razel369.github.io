# 011_path_join

1. Set system from `../SYSTEM.txt` (or use COMBINED below).
2. Copy the USER prompt.
3. Save model reply to `../replies/011_path_join.txt`.
4. Grade: `python3 interface/grade_reply.py --task 011_path_join --reply interface/replies/011_path_join.txt`

## USER prompt

```
Task: 011_path_join
Attempt: 1/1

## Failing logs (symptoms only)
```
F                                                                        [100%]
=================================== FAILURES ===================================
___________________________________ test_sep ___________________________________
tests/test_smoke.py:8: in test_sep
    assert out.replace("\\", "/") == "/tmp/data/file.txt"
E   AssertionError: assert '/tmp/datafile.txt' == '/tmp/data/file.txt'
E     
E     - /tmp/data/file.txt
E     ?          -
E     + /tmp/datafile.txt
=========================== short test summary info ============================
FAILED tests/test_smoke.py::test_sep - AssertionError: assert '/tmp/datafile....
1 failed in 0.01s
```

## Project files

### paths.py
```python
from pathlib import Path

def join_path(base: str, name: str) -> str:
    """Join directory base with file name."""
    return base + name
```

## Your job
Fix the bug so the failing tests would pass.
Reply with <<<FILE ...>>> <<<END>>> blocks only.
Most likely file to edit: `paths.py`
```
