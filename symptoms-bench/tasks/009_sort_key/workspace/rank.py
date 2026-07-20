def longest_first(words: list[str]) -> list[str]:
    """Return words sorted by length descending, stable for ties."""
    return sorted(words, key=len)  # BUG: missing reverse=True
