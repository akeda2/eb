#!/bin/bash
#
# Build and install:
#
# Uses pyinstaller:
if [ ! $(command -v pyinstaller) ]; then
	if [ ! $(command -v pip3)]; then
		echo "pip3 not installed...installing..."
		sudo apt install python3-pip || echo "FAILED!"
	fi
	sudo pip3 install pyinstaller || sudo pip3 install pyinstaller --break-system-packages && echo "Installed pyinstaller"
else
	sudo pip3 install --upgrade pyinstaller || sudo pip3 install pyinstaller --break-system-packages && "Updated pyinstaller"
fi
echo "Running make..."
make clean && make || echo "FAILED!"
printf "\n\nRun 'sudo make install', to install to /usr/local/bin\n\n"
