# 007_integer_division

1. Set system from `../SYSTEM.txt` (or use COMBINED below).
2. Copy the USER prompt.
3. Save model reply to `../replies/007_integer_division.txt`.
4. Grade: `python3 interface/grade_reply.py --task 007_integer_division --reply interface/replies/007_integer_division.txt`

## USER prompt

```
Task: 007_integer_division
Attempt: 1/1

## Failing logs (symptoms only)
```
F                                                                        [100%]
=================================== FAILURES ===================================
__________________________________ test_half ___________________________________
tests/test_smoke.py:7: in test_half
    assert abs(mean([1, 2]) - 1.5) < 1e-9
E   assert 0.5 < 1e-09
E    +  where 0.5 = abs((1 - 1.5))
E    +    where 1 = mean([1, 2])
=========================== short test summary info ============================
FAILED tests/test_smoke.py::test_half - assert 0.5 < 1e-09
1 failed in 0.01s
```

## Project files

### stats.py
```python
def mean(nums: list[float]) -> float:
    """Return arithmetic mean."""
    return sum(nums) // len(nums)
```

## Your job
Fix the bug so the failing tests would pass.
Reply with <<<FILE ...>>> <<<END>>> blocks only.
Most likely file to edit: `stats.py`
```
