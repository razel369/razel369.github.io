"""Symptoms Debugger — log-only repair loop."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# Allow importing sibling harness helpers when run as a script
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
from run_eval import (  # noqa: E402
    SYSTEM,
    extract_file_map,
)


@dataclass
class AttemptRecord:
    attempt: int
    passed: bool
    logs: str
    raw: str
    error: str | None = None


@dataclass
class RepairResult:
    passed: bool
    attempts_used: int
    final_workspace: Path | None
    history: list[AttemptRecord] = field(default_factory=list)


def run_pytest(workspace: Path, test_path: Path) -> tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_path), "-q", "--tb=short"],
        cwd=workspace,
        capture_output=True,
        text=True,
    )
    logs = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, logs


class SymptomsDebugger:
    """Plugin core: diagnose from logs, patch, re-run, repeat."""

    def __init__(self, generate_fn, max_attempts: int = 5):
        """
        generate_fn(system: str, user: str) -> str
        """
        self.generate_fn = generate_fn
        self.max_attempts = max_attempts

    def _prompt(self, files: dict[str, str], logs: str, attempt: int, prior: list[AttemptRecord]) -> str:
        parts = [
            f"Attempt {attempt}/{self.max_attempts}",
            "Failing logs (symptoms only):",
            "```",
            logs.strip() or "(no output)",
            "```",
            "",
            "Current project files:",
        ]
        for rel, content in files.items():
            parts.append(f"\n----- FILE: {rel} -----\n{content}")
        if prior:
            parts.append("\nPrevious attempts failed. Do NOT repeat the same broken patch.")
            parts.append("Use the newest logs above; invent a different fix hypothesis.")
        parts.append(
            "\nRespond with <<<FILE path>>> ... <<<END>>> blocks containing FULL fixed file contents."
        )
        return "\n".join(parts)

    def repair(
        self,
        workspace_src: Path,
        initial_logs: str,
        *,
        grade_tests: Path | None = None,
        smoke_tests: Path | None = None,
    ) -> RepairResult:
        """Iteratively repair workspace_src using logs as the only symptom channel."""
        workspace_src = workspace_src.resolve()
        history: list[AttemptRecord] = []

        with tempfile.TemporaryDirectory(prefix="symptoms-dbg-") as tmp:
            work = Path(tmp) / "workspace"
            shutil.copytree(
                workspace_src,
                work,
                ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"),
            )
            logs = initial_logs
            py_files = [p.name for p in sorted(work.glob("*.py"))]
            default_py = py_files[0] if len(py_files) == 1 else None

            for attempt in range(1, self.max_attempts + 1):
                files = {
                    p.relative_to(work).as_posix(): p.read_text(encoding="utf-8")
                    for p in sorted(work.rglob("*"))
                    if p.is_file()
                    and p.suffix in {".py", ".md"}
                    and "tests" not in p.parts
                    and "__pycache__" not in p.parts
                }
                user = self._prompt(files, logs, attempt, history)
                raw = ""
                error = None
                try:
                    raw = self.generate_fn(SYSTEM, user)
                    patch = extract_file_map(raw, default_py=default_py)
                    for rel, content in patch.items():
                        rel_path = Path(rel)
                        if rel_path.is_absolute() or ".." in rel_path.parts:
                            continue
                        target = work / rel_path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(content, encoding="utf-8")
                except Exception as exc:  # noqa: BLE001
                    error = f"{type(exc).__name__}: {exc}"

                # Feedback must use tests inside the working copy so imports
                # resolve to the patched sources (not the original buggy tree).
                feedback_tests = work / "tests"
                if smoke_tests is not None:
                    # Rare override: caller-provided tests copied into work
                    feedback_tests = smoke_tests
                if feedback_tests.exists():
                    passed_smoke, new_logs = run_pytest(work, feedback_tests)
                else:
                    passed_smoke, new_logs = False, "no tests found for feedback"

                # If smoke passed and we have hidden grade tests, verify those too
                passed = passed_smoke
                grade_logs = ""
                if passed_smoke and grade_tests is not None:
                    # grade.py style: copy workspace + hidden tests
                    with tempfile.TemporaryDirectory(prefix="symptoms-grade-") as gtmp:
                        gpath = Path(gtmp)
                        gwork = gpath / "workspace"
                        shutil.copytree(work, gwork)
                        ghidden = gpath / "hidden_tests"
                        shutil.copytree(grade_tests, ghidden)
                        passed, grade_logs = run_pytest(gpath, ghidden)
                        if not passed:
                            new_logs = grade_logs

                history.append(
                    AttemptRecord(
                        attempt=attempt,
                        passed=passed,
                        logs=new_logs if not passed else logs,
                        raw=raw,
                        error=error,
                    )
                )
                if passed:
                    final = Path(tempfile.mkdtemp(prefix="symptoms-final-"))
                    shutil.copytree(work, final / "workspace")
                    return RepairResult(
                        passed=True,
                        attempts_used=attempt,
                        final_workspace=final / "workspace",
                        history=history,
                    )
                logs = new_logs  # feed symptoms forward

            return RepairResult(
                passed=False,
                attempts_used=self.max_attempts,
                final_workspace=None,
                history=history,
            )
