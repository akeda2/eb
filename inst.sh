#!/bin/bash
echo "Installing eb to /usr/local/bin/eb..."
[ -f eb.py ] && sudo cp --remove-destination eb.py /usr/local/bin/eb
