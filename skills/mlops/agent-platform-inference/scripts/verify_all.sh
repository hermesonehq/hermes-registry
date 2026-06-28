#!/bin/bash
set -e

# Create a temporary directory for the virtual environment
VENV_DIR=$(mktemp -d -t venv_verify.XXXXXX)
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Trap to ensure cleanup happens on exit
cleanup() {
  echo "Cleaning up virtual environment..."
  deactivate 2>/dev/null || true
  rm -rf "$VENV_DIR"
}
trap cleanup EXIT

echo "Installing requirements..."
pip install -q -r scripts/requirements.txt

echo "Running verification tests..."
FAILED=0

# Iterate directly over the files in the scripts directory
for script in scripts/*.py; do
  echo "Running $script..."
  if python3 "$script" > /dev/null 2>&1; then
    echo "  PASS: $script"
  else
    echo "  FAIL: $script"
    python3 "$script" # Run again to show output
    FAILED=1
  fi
done

if [[ $FAILED -eq 0 ]]; then
  echo "All scripts passed verification!"
  exit 0
else
  echo "Some scripts failed verification."
  exit 1
fi
