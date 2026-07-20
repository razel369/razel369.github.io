def apply_discount(price: float, discount: float) -> float:
    """Apply fractional discount in [0, 1], e.g. 0.2 = 20% off."""
    return price - discount  # BUG: wrong operator / formula
