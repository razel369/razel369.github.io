#!/usr/bin/env python3
"""Create SymptomsBench planted-bug tasks."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "tasks"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def task(
    tid: str,
    slug: str,
    difficulty: str,
    tags: list[str],
    description: str,
    bug_summary: str,
    workspace_files: dict[str, str],
    hidden_tests: str,
    smoke_failing_test: str,
) -> None:
    base = ROOT / f"{tid}_{slug}"
    if base.exists():
        for p in base.rglob("*"):
            if p.is_file():
                p.unlink()
    meta = {
        "id": f"{tid}_{slug}",
        "difficulty": difficulty,
        "tags": tags,
        "description": description,
    }
    manifest = {"bug_summary": bug_summary}
    write(base / "meta.json", json.dumps(meta, indent=2) + "\n")
    write(base / "bug_manifest.json", json.dumps(manifest, indent=2) + "\n")
    for rel, content in workspace_files.items():
        write(base / "workspace" / rel, content)
    write(base / "hidden_tests" / "test_correctness.py", hidden_tests)
    write(base / "workspace" / "tests" / "test_smoke.py", smoke_failing_test)
    # Agent-visible README with NO bug spoilers
    write(
        base / "workspace" / "README.md",
        f"""
        # {slug.replace('_', ' ').title()}

        Run smoke tests:

        ```bash
        python -m pytest tests/ -q
        ```
        """,
    )


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)

    task(
        "001",
        "off_by_one",
        "easy",
        ["loops", "indexing"],
        "Sum should include the last index.",
        "range(len(nums)-1) skips the last element; should be range(len(nums)).",
        {
            "sum_window.py": '''
            def sum_all(nums: list[int]) -> int:
                """Return the sum of every element in nums."""
                total = 0
                for i in range(len(nums) - 1):
                    total += nums[i]
                return total
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from sum_window import sum_all

        def test_basic():
            assert sum_all([1, 2, 3, 4]) == 10

        def test_single():
            assert sum_all([7]) == 7

        def test_empty():
            assert sum_all([]) == 0
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from sum_window import sum_all

        def test_sum_includes_last():
            assert sum_all([1, 2, 3, 4]) == 10
        ''',
    )

    task(
        "002",
        "wrong_operator",
        "easy",
        ["operators"],
        "Discount application subtracts instead of multiplying fraction.",
        "Uses price - discount instead of price * (1 - discount).",
        {
            "pricing.py": '''
            def apply_discount(price: float, discount: float) -> float:
                """Apply fractional discount in [0, 1], e.g. 0.2 = 20% off."""
                return price - discount
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from pricing import apply_discount

        def test_twenty_percent():
            assert abs(apply_discount(100.0, 0.2) - 80.0) < 1e-9

        def test_zero():
            assert apply_discount(50.0, 0.0) == 50.0

        def test_full():
            assert apply_discount(40.0, 1.0) == 0.0
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from pricing import apply_discount

        def test_discount():
            assert abs(apply_discount(100.0, 0.2) - 80.0) < 1e-9
        ''',
    )

    task(
        "003",
        "wrong_variable",
        "easy",
        ["variables"],
        "Clamp uses raw value instead of clamped result.",
        "Returns x instead of the clamped lo/hi value.",
        {
            "clamp.py": '''
            def clamp(x: float, lo: float, hi: float) -> float:
                """Clamp x into [lo, hi]."""
                if x < lo:
                    result = lo
                elif x > hi:
                    result = hi
                else:
                    result = x
                return x
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from clamp import clamp

        def test_below():
            assert clamp(-5, 0, 10) == 0

        def test_above():
            assert clamp(99, 0, 10) == 10

        def test_inside():
            assert clamp(3, 0, 10) == 3
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from clamp import clamp

        def test_clamp_low():
            assert clamp(-5, 0, 10) == 0
        ''',
    )

    task(
        "004",
        "case_sensitive",
        "easy",
        ["strings"],
        "Membership check is case-sensitive.",
        "Compares token directly without lowercasing.",
        {
            "filter_words.py": '''
            def contains_banned(text: str, banned: list[str]) -> bool:
                """Return True if any banned word appears (case-insensitive)."""
                tokens = text.split()
                for token in tokens:
                    if token in banned:
                        return True
                return False
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from filter_words import contains_banned

        def test_case():
            assert contains_banned("Hello WORLD", ["world"]) is True

        def test_absent():
            assert contains_banned("hi there", ["bye"]) is False
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from filter_words import contains_banned

        def test_banned_casefold():
            assert contains_banned("Hello WORLD", ["world"]) is True
        ''',
    )

    task(
        "005",
        "dict_key",
        "easy",
        ["dicts"],
        "Histogram uses wrong key when counting.",
        "Increments counts[item] but stores under counts[0] mistakenly via wrong key var.",
        {
            "histogram.py": '''
            def count_items(items: list[str]) -> dict[str, int]:
                """Count occurrences of each item."""
                counts: dict[str, int] = {}
                for item in items:
                    key = items[0]
                    counts[key] = counts.get(key, 0) + 1
                return counts
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from histogram import count_items

        def test_counts():
            assert count_items(["a", "b", "a"]) == {"a": 2, "b": 1}

        def test_empty():
            assert count_items([]) == {}
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from histogram import count_items

        def test_hist():
            assert count_items(["a", "b", "a"]) == {"a": 2, "b": 1}
        ''',
    )

    task(
        "006",
        "mutable_default",
        "medium",
        ["defaults", "gotchas"],
        "Append helper leaks state across calls via mutable default.",
        "def append_item(item, bucket=[]): mutates shared list.",
        {
            "bags.py": '''
            def append_item(item: str, bucket: list[str] | None = []) -> list[str]:
                """Append item to bucket and return it. Empty bucket by default."""
                bucket.append(item)
                return bucket
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from bags import append_item

        def test_independent_calls():
            a = append_item("x")
            b = append_item("y")
            assert a == ["x"]
            assert b == ["y"]
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from bags import append_item

        def test_no_leak():
            a = append_item("x")
            b = append_item("y")
            assert a == ["x"]
            assert b == ["y"]
        ''',
    )

    task(
        "007",
        "integer_division",
        "easy",
        ["math"],
        "Average should be float mean, not floor division.",
        "Uses // instead of /.",
        {
            "stats.py": '''
            def mean(nums: list[float]) -> float:
                """Return arithmetic mean."""
                return sum(nums) // len(nums)
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from stats import mean

        def test_mean():
            assert abs(mean([1, 2]) - 1.5) < 1e-9

        def test_ints():
            assert mean([2, 2, 2]) == 2
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from stats import mean

        def test_half():
            assert abs(mean([1, 2]) - 1.5) < 1e-9
        ''',
    )

    task(
        "008",
        "early_return",
        "medium",
        ["loops", "controlflow"],
        "Finder returns on first mismatch instead of continuing.",
        "Returns False inside loop on first non-match; should only return True when found.",
        {
            "find.py": '''
            def find_first(preds: list[int], target: int) -> int | None:
                """Return index of target or None."""
                for i, value in enumerate(preds):
                    if value != target:
                        return None
                    return i
                return None
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from find import find_first

        def test_later():
            assert find_first([9, 8, 7], 7) == 2

        def test_missing():
            assert find_first([1, 2], 5) is None

        def test_first():
            assert find_first([3, 1], 3) == 0
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from find import find_first

        def test_find():
            assert find_first([9, 8, 7], 7) == 2
        ''',
    )

    task(
        "009",
        "sort_key",
        "medium",
        ["sorting"],
        "Sort by length descending is reversed incorrectly.",
        "Uses key=len without reverse=True (or reverse wrong).",
        {
            "rank.py": '''
            def longest_first(words: list[str]) -> list[str]:
                """Return words sorted by length descending, stable for ties."""
                return sorted(words, key=len)
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from rank import longest_first

        def test_order():
            assert longest_first(["a", "bbbb", "cc"]) == ["bbbb", "cc", "a"]
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from rank import longest_first

        def test_long_first():
            assert longest_first(["a", "bbbb", "cc"]) == ["bbbb", "cc", "a"]
        ''',
    )

    task(
        "010",
        "recursion_base",
        "medium",
        ["recursion"],
        "Factorial base case wrong for 0.",
        "Returns 0 for n==0 instead of 1.",
        {
            "fact.py": '''
            def factorial(n: int) -> int:
                """Compute n! for n >= 0."""
                if n == 0:
                    return 0
                return n * factorial(n - 1)
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from fact import factorial

        def test_zero():
            assert factorial(0) == 1

        def test_five():
            assert factorial(5) == 120
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from fact import factorial

        def test_fact0():
            assert factorial(0) == 1
        ''',
    )

    task(
        "011",
        "path_join",
        "medium",
        ["paths"],
        "Join uses string plus and drops separators.",
        "base + name instead of proper join.",
        {
            "paths.py": '''
            from pathlib import Path

            def join_path(base: str, name: str) -> str:
                """Join directory base with file name."""
                return base + name
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from paths import join_path

        def test_join():
            out = join_path("/tmp/data", "file.txt")
            assert out.replace("\\\\", "/") == "/tmp/data/file.txt"
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from paths import join_path

        def test_sep():
            out = join_path("/tmp/data", "file.txt")
            assert out.replace("\\\\", "/") == "/tmp/data/file.txt"
        ''',
    )

    task(
        "012",
        "unique_preserve",
        "medium",
        ["sets", "order"],
        "Dedup should preserve first-seen order.",
        "Returns sorted(set(...)) which alphabetizes instead of preserving order.",
        {
            "unique.py": '''
            def unique_preserve(items: list[str]) -> list[str]:
                """Deduplicate while preserving first-seen order."""
                return sorted(set(items))
            '''
        },
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workspace"))
        from unique import unique_preserve

        def test_order():
            assert unique_preserve(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]
        ''',
        '''
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from unique import unique_preserve

        def test_preserve():
            assert unique_preserve(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]
        ''',
    )

    print(f"Created tasks under {ROOT}")
    print("Tasks:", sorted(p.name for p in ROOT.iterdir() if p.is_dir()))


if __name__ == "__main__":
    main()
