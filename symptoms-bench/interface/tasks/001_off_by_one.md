# 001_off_by_one

1. Set system from `../SYSTEM.txt` (or use COMBINED below).
2. Copy the USER prompt.
3. Save model reply to `../replies/001_off_by_one.txt`.
4. Grade: `python3 interface/grade_reply.py --task 001_off_by_one --reply interface/replies/001_off_by_one.txt`

## USER prompt

```
Task: 001_off_by_one
Attempt: 1/1

## Failing logs (symptoms only)
```
F                                                                        [100%]
=================================== FAILURES ===================================
____________________________ test_sum_includes_last ____________________________
tests/test_smoke.py:7: in test_sum_includes_last
    assert sum_all([1, 2, 3, 4]) == 10
E   assert 6 == 10
E    +  where 6 = sum_all([1, 2, 3, 4])
=========================== short test summary info ============================
FAILED tests/test_smoke.py::test_sum_includes_last - assert 6 == 10
1 failed in 0.01s
```

## Project files

### sum_window.py
```python
def sum_all(nums: list[int]) -> int:
    """Return the sum of every element in nums."""
    total = 0
    for i in range(len(nums) - 1):
        total += nums[i]
    return total
```

## Your job
Fix the bug so the failing tests would pass.
Reply with <<<FILE ...>>> <<<END>>> blocks only.
Most likely file to edit: `sum_window.py`
```
