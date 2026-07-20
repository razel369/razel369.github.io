def sum_all(nums: list[int]) -> int:
    """Return the sum of every element in nums."""
    total = 0
    for i in range(len(nums) - 1):  # BUG: off-by-one
        total += nums[i]
    return total
