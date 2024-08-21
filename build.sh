#!/bin/bash
#
# Build and install:
APPNAME="eb"
#
# Uses pyinstaller:

# Check for the existence of the venv module
if python3 -m venv --help &> /dev/null; then
    echo "Python venv is installed."
else
    echo "Python venv is not installed!"
    echo "If you are using Debian/Ubuntu/etc, install via:"
    echo "sudo apt update; sudo apt install python3-venv"
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install the dependencies
pip3 install -r requirements.txt

# Run PyInstaller to create the executable
pyinstaller --onefile "$APPNAME".py --clean -F --noupx

# Move the executable to /usr/local/bin
# You might need to run this script as root to have permission for this operation
echo "Moving the executable to /usr/local/bin"
sudo install -v -m 755 dist/"$APPNAME" /usr/local/bin/"$APPNAME"

# Deactivate the virtual environment
deactivate

# Remove the build files:
rm -rfv ./dist/ ./build/ ./*.spec ./*.pyc ./*.log "$APPNAME".spec dist/ "$APPNAME"

echo "Build complete. Installed to /usr/local/bin/$APPNAME"