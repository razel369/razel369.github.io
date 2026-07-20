def count_items(items: list[str]) -> dict[str, int]:
    """Count occurrences of each item."""
    counts: dict[str, int] = {}
    for item in items:
        key = items[0]  # BUG: always first item
        counts[key] = counts.get(key, 0) + 1
    return counts
