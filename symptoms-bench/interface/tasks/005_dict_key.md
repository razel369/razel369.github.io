# 005_dict_key

1. Set system from `../SYSTEM.txt` (or use COMBINED below).
2. Copy the USER prompt.
3. Save model reply to `../replies/005_dict_key.txt`.
4. Grade: `python3 interface/grade_reply.py --task 005_dict_key --reply interface/replies/005_dict_key.txt`

## USER prompt

```
Task: 005_dict_key
Attempt: 1/1

## Failing logs (symptoms only)
```
F                                                                        [100%]
=================================== FAILURES ===================================
__________________________________ test_hist ___________________________________
tests/test_smoke.py:7: in test_hist
    assert count_items(["a", "b", "a"]) == {"a": 2, "b": 1}
E   AssertionError: assert {'a': 3} == {'a': 2, 'b': 1}
E     
E     Differing items:
E     {'a': 3} != {'a': 2}
E     Right contains 1 more item:
E     {'b': 1}
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_smoke.py::test_hist - AssertionError: assert {'a': 3} == {'...
1 failed in 0.01s
```

## Project files

### histogram.py
```python
def count_items(items: list[str]) -> dict[str, int]:
    """Count occurrences of each item."""
    counts: dict[str, int] = {}
    for item in items:
        key = items[0]
        counts[key] = counts.get(key, 0) + 1
    return counts
```

## Your job
Fix the bug so the failing tests would pass.
Reply with <<<FILE ...>>> <<<END>>> blocks only.
Most likely file to edit: `histogram.py`
```
