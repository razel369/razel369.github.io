# 002_wrong_operator

1. Set system from `../SYSTEM.txt` (or use COMBINED below).
2. Copy the USER prompt.
3. Save model reply to `../replies/002_wrong_operator.txt`.
4. Grade: `python3 interface/grade_reply.py --task 002_wrong_operator --reply interface/replies/002_wrong_operator.txt`

## USER prompt

```
Task: 002_wrong_operator
Attempt: 1/1

## Failing logs (symptoms only)
```
F                                                                        [100%]
=================================== FAILURES ===================================
________________________________ test_discount _________________________________
tests/test_smoke.py:7: in test_discount
    assert abs(apply_discount(100.0, 0.2) - 80.0) < 1e-9
E   assert 19.799999999999997 < 1e-09
E    +  where 19.799999999999997 = abs((99.8 - 80.0))
E    +    where 99.8 = apply_discount(100.0, 0.2)
=========================== short test summary info ============================
FAILED tests/test_smoke.py::test_discount - assert 19.799999999999997 < 1e-09
1 failed in 0.01s
```

## Project files

### pricing.py
```python
def apply_discount(price: float, discount: float) -> float:
    """Apply fractional discount in [0, 1], e.g. 0.2 = 20% off."""
    return price - discount
```

## Your job
Fix the bug so the failing tests would pass.
Reply with <<<FILE ...>>> <<<END>>> blocks only.
Most likely file to edit: `pricing.py`
```
