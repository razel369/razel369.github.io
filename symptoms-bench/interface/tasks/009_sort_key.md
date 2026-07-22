# 009_sort_key

1. Set system from `../SYSTEM.txt` (or use COMBINED below).
2. Copy the USER prompt.
3. Save model reply to `../replies/009_sort_key.txt`.
4. Grade: `python3 interface/grade_reply.py --task 009_sort_key --reply interface/replies/009_sort_key.txt`

## USER prompt

```
Task: 009_sort_key
Attempt: 1/1

## Failing logs (symptoms only)
```
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________________ test_long_first ________________________________
tests/test_smoke.py:7: in test_long_first
    assert longest_first(["a", "bbbb", "cc"]) == ["bbbb", "cc", "a"]
E   AssertionError: assert ['a', 'cc', 'bbbb'] == ['bbbb', 'cc', 'a']
E     
E     At index 0 diff: 'a' != 'bbbb'
E     Use -v to get more diff
=========================== short test summary info ============================
FAILED tests/test_smoke.py::test_long_first - AssertionError: assert ['a', 'c...
1 failed in 0.01s
```

## Project files

### rank.py
```python
def longest_first(words: list[str]) -> list[str]:
    """Return words sorted by length descending, stable for ties."""
    return sorted(words, key=len)
```

## Your job
Fix the bug so the failing tests would pass.
Reply with <<<FILE ...>>> <<<END>>> blocks only.
Most likely file to edit: `rank.py`
```
