"""Path setup for sector-analyst tests."""

import sys
from pathlib import Path

_tests_dir = Path(__file__).resolve().parent
_scripts_dir = _tests_dir.parent

# Add scripts/ to sys.path so tests can import analyze_sector_rotation
sys.path.insert(0, str(_scripts_dir))
# Add tests/ to sys.path so tests can import helpers
sys.path.insert(0, str(_tests_dir))
