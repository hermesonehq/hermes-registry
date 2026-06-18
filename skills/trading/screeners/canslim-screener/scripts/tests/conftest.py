"""Shared fixtures for CANSLIM Screener tests"""

import os
import sys

# Add scripts directory to path so modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Add calculators subdirectory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "calculators"))
# Add tests directory to path so helpers can be imported
sys.path.insert(0, os.path.dirname(__file__))
