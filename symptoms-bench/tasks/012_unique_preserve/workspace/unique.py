def unique_preserve(items: list[str]) -> list[str]:
    """Deduplicate while preserving first-seen order."""
    return sorted(set(items))  # BUG: sorts instead of preserving order
