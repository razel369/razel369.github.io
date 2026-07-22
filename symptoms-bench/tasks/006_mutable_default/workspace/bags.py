def append_item(item: str, bucket: list[str] | None = []) -> list[str]:
    """Append item to bucket and return it. Empty bucket by default."""
    bucket.append(item)
    return bucket
