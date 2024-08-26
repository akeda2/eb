# eb
Line Ebitor
### Installation:
#### Build (with venv):
```
./build.sh
```
#### Or manually:
Needs pyinstaller:
```
pip3 install pyinstaller
```
Then:
```
make
make install
```
#### Cleanup and rebuild (if python/OS upgrade breaks stuff)
```
make clean
./build.sh
```
#### Install as it is:
```
./inst.sh
(it just copies eb.py to /usr/local/bin/eb)
```