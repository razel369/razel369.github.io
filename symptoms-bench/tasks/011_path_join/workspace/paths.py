from pathlib import Path

def join_path(base: str, name: str) -> str:
    """Join directory base with file name."""
    return base + name  # BUG: missing separator
