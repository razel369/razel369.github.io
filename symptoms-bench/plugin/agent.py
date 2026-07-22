"""Symptoms Debugger — log-only repair loop."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "plugin"))

from prompts import SYSTEM, build_task_user_prompt  # noqa: E402
from run_eval import extract_file_map  # noqa: E402


@dataclass
class AttemptRecord:
    attempt: int
    passed: bool
    logs: str
    raw: str
    error: str | None = None
    patched_files: list[str] = field(default_factory=list)


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


def _is_placeholder(content: str) -> bool:
    s = content.strip().lower()
    if len(s) < 8:
        return True
    bad = (
        "... corrected implementation ...",
        "entire fixed file contents",
        "pass  # todo",
        "full fixed source",
    )
    return any(b in s for b in bad)


class SymptomsDebugger:
    """Plugin core: diagnose from logs, patch, re-run, repeat."""

    def __init__(self, generate_fn, max_attempts: int = 5):
        self.generate_fn = generate_fn
        self.max_attempts = max_attempts

    def repair(
        self,
        workspace_src: Path,
        initial_logs: str,
        *,
        grade_tests: Path | None = None,
        smoke_tests: Path | None = None,
        task_id: str | None = None,
    ) -> RepairResult:
        workspace_src = workspace_src.resolve()
        history: list[AttemptRecord] = []
        task_id = task_id or workspace_src.parent.name

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
                    for p in sorted(work.rglob("*.py"))
                    if p.is_file()
                    and "tests" not in p.parts
                    and "__pycache__" not in p.parts
                }
                prior_note = None
                if history:
                    last = history[-1]
                    bits = [
                        "Previous attempt failed. Do not repeat the same broken patch.",
                        f"Last failing logs tail:\n```\n{last.logs.strip()[-800:]}\n```",
                    ]
                    if last.patched_files:
                        bits.append(
                            "Files you changed last time: "
                            + ", ".join(last.patched_files)
                        )
                    if last.error:
                        bits.append(f"Scaffold error: {last.error}")
                    prior_note = "\n".join(bits)

                user = build_task_user_prompt(
                    task_id,
                    logs,
                    files,
                    attempt=attempt,
                    max_attempts=self.max_attempts,
                    hint_source=default_py,
                    prior_note=prior_note,
                )
                raw = ""
                error = None
                patched: list[str] = []
                try:
                    raw = self.generate_fn(SYSTEM, user)
                    patch = extract_file_map(raw, default_py=default_py)
                    filtered = {
                        rel: content
                        for rel, content in patch.items()
                        if "tests" not in Path(rel).parts
                        and not Path(rel).name.startswith("test_")
                        and not _is_placeholder(content)
                    }
                    if not filtered:
                        raise ValueError(
                            "no valid source patch (tests-only, empty, or placeholder)"
                        )
                    for rel, content in filtered.items():
                        rel_path = Path(rel)
                        if rel_path.is_absolute() or ".." in rel_path.parts:
                            continue
                        # If model invents a wrong name but we know the only source file,
                        # redirect to it when content looks like python source.
                        if (
                            default_py
                            and rel_path.name != default_py
                            and not (work / rel_path).exists()
                            and "def " in content
                        ):
                            rel_path = Path(default_py)
                        target = work / rel_path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(content, encoding="utf-8")
                        patched.append(rel_path.as_posix())
                    if not patched:
                        raise ValueError("patch produced no writable source files")
                except Exception as exc:  # noqa: BLE001
                    error = f"{type(exc).__name__}: {exc}"

                feedback_tests = work / "tests"
                if smoke_tests is not None:
                    feedback_tests = smoke_tests
                if feedback_tests.exists():
                    passed_smoke, new_logs = run_pytest(work, feedback_tests)
                else:
                    passed_smoke, new_logs = False, "no tests found for feedback"

                passed = passed_smoke
                if passed_smoke and grade_tests is not None:
                    with tempfile.TemporaryDirectory(prefix="symptoms-grade-") as gtmp:
                        gpath = Path(gtmp)
                        shutil.copytree(work, gpath / "workspace")
                        shutil.copytree(grade_tests, gpath / "hidden_tests")
                        passed, grade_logs = run_pytest(gpath, gpath / "hidden_tests")
                        if not passed:
                            new_logs = grade_logs

                history.append(
                    AttemptRecord(
                        attempt=attempt,
                        passed=passed,
                        logs=new_logs if not passed else logs,
                        raw=raw,
                        error=error,
                        patched_files=patched,
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
                logs = new_logs

            return RepairResult(
                passed=False,
                attempts_used=self.max_attempts,
                final_workspace=None,
                history=history,
            )
