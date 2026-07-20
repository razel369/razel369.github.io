def factorial(n: int) -> int:
    """Compute n! for n >= 0."""
    if n == 0:
        return 0  # BUG: should be 1
    return n * factorial(n - 1)
