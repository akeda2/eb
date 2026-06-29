#!/bin/bash
#
APPNAME="eb"
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$SCRIPT_DIR"

# Check for the existence of the venv module
if python3 -m venv --help &> /dev/null; then
    echo "Python venv is installed."
else
    echo "Python venv is not installed!"
    echo "If you are using Debian/Ubuntu/etc, install via:"
    echo "sudo apt update; sudo apt install python3-venv"
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate
trap 'deactivate 2>/dev/null || true' EXIT

# Install the dependencies
python -m pip install --upgrade pip
python -m pip install -e "$REPO_ROOT"
python -m pip install -r requirements.txt

# Run tests from repository root before building/installing.
echo "Running test suite..."
(cd "$REPO_ROOT" && python -m unittest discover -s tests -v)

# Run PyInstaller to create the executable
pyinstaller --onefile "$APPNAME".py --clean -F --noupx

# Move the executable to /usr/local/bin
echo "Moving the executable to /usr/local/bin"
sudo install -v -m 755 dist/"$APPNAME" /usr/local/bin/"$APPNAME"

# Remove the build files:
rm -rfv ./dist/ ./build/
rm -fv ./*.spec ./*.pyc ./*.log

echo "Build complete. Installed to /usr/local/bin/$APPNAME"