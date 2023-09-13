#!/bin/bash
#
# Build and install:
#
# Uses pyinstaller:
if [ ! $(command -v pyinstaller) ]; then
	if [ ! $(command -v pip3)]; then
		sudo apt install python3-pip
	fi
	sudo pip3 install pyinstaller --break-system-packages
else
	sudo pip3 install --upgrade pyinstaller --break-system-packages
fi

make clean && make
printf "\n\nRun 'sudo make install', to install to /usr/local/bin\n"
