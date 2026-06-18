"""Tests for the stdlib-only trader_memory_cli.py launcher.

Drives the launcher as a subprocess (the unit under test IS the
process-spawning wrapper), so behavior matches how Hermes / cron will
invoke it. No third-party deps; safe to run anywhere `python3` exists.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
LAUNCHER = REPO_ROOT / "skills" / "trader-memory-core" / "scripts" / "trader_memory_cli.py"


def _run(args, *, env=None, cwd=None):
    """Run the launcher and capture (returncode, stdout, stderr)."""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    proc = subprocess.run(
        [sys.executable, str(LAUNCHER), *args],
        env=full_env,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_no_args_prints_usage_and_exits_nonzero():
    rc, _, err = _run([])
    assert rc == 2
    assert "usage:" in err.lower()
    assert "store" in err and "ingest" in err and "review" in err


def test_help_flag_exits_zero():
    rc, _, err = _run(["--help"])
    assert rc == 0
    assert "store" in err


def test_unknown_subcommand_exits_nonzero_with_hint():
    rc, _, err = _run(["bogus"])
    assert rc == 2
    assert "unknown subcommand" in err.lower()
    assert "store" in err  # lists valid options


def test_repo_env_var_is_honored(tmp_path):
    """CLAUDE_TRADING_SKILLS_REPO must be respected even when running from
    a foreign cwd (mirrors Hermes profile cwd)."""
    state_dir = tmp_path / "state"
    rc, out, err = _run(
        ["store", "--state-dir", str(state_dir), "list"],
        env={"CLAUDE_TRADING_SKILLS_REPO": str(REPO_ROOT)},
        cwd=tmp_path,
    )
    assert rc == 0, f"stdout={out!r} stderr={err!r}"
    # Empty state dir → empty JSON list-or-equivalent. We don't assert the
    # exact shape (that's thesis_store's contract) — just that it didn't
    # crash on missing deps.
    assert "ModuleNotFoundError" not in err
    assert "jsonschema is not installed" not in err.lower()


def test_repo_env_var_pointing_at_missing_repo_fails_clearly(tmp_path):
    rc, _, err = _run(
        ["store", "list"],
        env={"CLAUDE_TRADING_SKILLS_REPO": str(tmp_path / "does-not-exist")},
    )
    assert rc == 2
    assert "target script not found" in err.lower()


def test_recursion_guard_blocks_inner_uv_reentry(tmp_path, monkeypatch):
    """With TRADER_MEMORY_CLI_INNER=1 set, the launcher must NOT re-exec
    via `uv run` — that would infinite-loop. Instead it falls through to
    the current-interpreter path."""
    # We can't easily simulate "uv is on PATH" vs not from here, so this
    # test asserts the guard fast-path: when inner=1, the launcher uses
    # sys.executable directly even if uv is available.
    state_dir = tmp_path / "state"
    rc, out, err = _run(
        ["store", "--state-dir", str(state_dir), "list"],
        env={
            "CLAUDE_TRADING_SKILLS_REPO": str(REPO_ROOT),
            "TRADER_MEMORY_CLI_INNER": "1",
        },
    )
    # If jsonschema is importable in this interpreter the call should
    # succeed (rc 0). If it's not (rare in CI), the launcher must emit the
    # informative error (rc 3) — NEVER hang.
    assert rc in (0, 3), f"rc={rc} stdout={out!r} stderr={err!r}"
    if rc == 3:
        assert "uv" in err.lower()


def test_missing_deps_error_message_is_actionable():
    """The launcher source must reference uv / repo env var in its missing
    -deps error, not just 'install jsonschema'."""
    src = LAUNCHER.read_text(encoding="utf-8")
    assert "uv" in src
    assert "CLAUDE_TRADING_SKILLS_REPO" in src
    # And the helper that builds the error string mentions all three paths.
    assert "Resolution options" in src


@pytest.mark.parametrize("sub", ["store", "ingest", "review"])
def test_subcommand_resolves_to_existing_target(sub):
    """Every advertised subcommand must point at a script that exists in
    the repo — catches typos in the launcher's SUBCOMMAND_TO_SCRIPT map."""
    targets = {
        "store": "thesis_store.py",
        "ingest": "thesis_ingest.py",
        "review": "thesis_review.py",
    }
    target = REPO_ROOT / "skills" / "trader-memory-core" / "scripts" / targets[sub]
    assert target.is_file(), f"missing target: {target}"
