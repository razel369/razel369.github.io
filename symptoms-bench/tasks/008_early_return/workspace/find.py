def find_first(preds: list[int], target: int) -> int | None:
    """Return index of target or None."""
    for i, value in enumerate(preds):
        if value != target:
            return None
        return i
    return None
