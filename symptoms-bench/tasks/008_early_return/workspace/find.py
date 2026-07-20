def find_first(preds: list[int], target: int) -> int | None:
    """Return index of target or None."""
    for i, value in enumerate(preds):
        if value != target:
            return None  # BUG: gives up too early
        return i
    return None
