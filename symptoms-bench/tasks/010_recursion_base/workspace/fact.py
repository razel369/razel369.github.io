def factorial(n: int) -> int:
    """Compute n! for n >= 0."""
    if n == 0:
        return 0
    return n * factorial(n - 1)
