def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp x into [lo, hi]."""
    if x < lo:
        result = lo
    elif x > hi:
        result = hi
    else:
        result = x
    return x  # BUG: should return result
