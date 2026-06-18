"""Test fixtures for dual-axis reviewer."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def reviewer_module():
    """Load run_dual_axis_review.py as a module for unit tests."""
    script_path = Path(__file__).resolve().parents[1] / "run_dual_axis_review.py"
    spec = importlib.util.spec_from_file_location("run_dual_axis_review", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load run_dual_axis_review.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
