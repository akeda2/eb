#!/bin/bash
#
# Copies the python script to /usr/local/bin without using pyinstaller
#
echo "Copying eb to /usr/local/bin/eb without using pyinstaller:"
[ -f eb.py ] && sudo cp --remove-destination eb.py /usr/local/bin/eb
