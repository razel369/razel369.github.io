def contains_banned(text: str, banned: list[str]) -> bool:
    """Return True if any banned word appears (case-insensitive)."""
    tokens = text.split()
    for token in tokens:
        if token in banned:  # BUG: case-sensitive
            return True
    return False
