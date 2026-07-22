"""Shared prompt text for SymptomsBench / Symptoms Debugger."""

SYSTEM = """You are Symptoms Debugger — a log-only bug-fixing agent.

You get:
1) failing test/traceback logs (symptoms)
2) the current project source files

You do NOT get a natural-language bug description. Diagnose only from symptoms.

## Output format (mandatory)

Return ONLY one or more file blocks. No markdown prose. No analysis.

<<<FILE relative/path.py>>>
entire fixed file contents
<<<END>>>

## Hard rules
- Edit the buggy SOURCE module only (never anything under tests/).
- Use the real filename from the project listing.
- Return the FULL file, not a partial diff.
- If unsure, still emit a complete best-guess fixed file.
- Do not wrap the blocks in ``` fences.
"""


def build_task_user_prompt(
    task_id: str,
    logs: str,
    files: dict[str, str],
    *,
    attempt: int = 1,
    max_attempts: int = 1,
    hint_source: str | None = None,
    prior_note: str | None = None,
) -> str:
    parts = [
        f"Task: {task_id}",
        f"Attempt: {attempt}/{max_attempts}",
        "",
        "## Failing logs (symptoms only)",
        "```",
        logs.strip() or "(empty)",
        "```",
        "",
        "## Project files",
    ]
    for rel, content in files.items():
        parts.append(f"\n### {rel}\n```python\n{content.rstrip()}\n```")
    if prior_note:
        parts.extend(["", "## Feedback from previous attempt", prior_note.strip()])
    parts.extend(
        [
            "",
            "## Your job",
            "Fix the bug so the failing tests would pass.",
            "Reply with <<<FILE ...>>> <<<END>>> blocks only.",
        ]
    )
    if hint_source:
        parts.append(f"Most likely file to edit: `{hint_source}`")
    return "\n".join(parts)


def combined_prompt(system: str, user: str) -> str:
    """For chat UIs without a separate system role."""
    return (
        "### SYSTEM INSTRUCTIONS\n"
        f"{system.strip()}\n\n"
        "### USER TASK\n"
        f"{user.strip()}\n"
    )
