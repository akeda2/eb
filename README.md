# eb
A primitive line ebitor
### Installation:
#### pipx:
```
sudo apt install pipx
pipx install .
```
#### pip:
```
pip3 install .
```
#### Build (creates/uses venv, uses pyinstaller and installs in /usr/local/bin/eb):
```
Navigate to 'eb' subdir:
cd eb
./build.sh
```
#### Or manually:
You'll have to manually install dependencies from ```requirements.txt```:
```
pip3 install -r requirements.txt
make
sudo make install
```
#### Install as it is:
Just copies eb.py to /usr/local/bin/eb. You'll have to manually install dependencies from ```requirements.txt```:
```
pip3 install -r requirements.txt 
./inst.sh
```
### Usage:
```
eb - a primitive line-ebitor. 'h' is help, 'q' is quit. Python version: 3.12.3
?h
Available commands:
p  - print the buffer with line numbers
pr - print the buffer with line endings visible (raw)
ph - print the buffer like pr but with hex values
pl - print the buffer without line numbers
m  - print the buffer one page at the time (more-style)
c  - print near Context of a line number
t  - print the last n lines of the buffer (tail-style)

a  - append one or more lines to the buffer
i  - insert a line into the buffer
d  - delete a line from the buffer
s  - substitute a line in the buffer
e  - edit a line in the buffer
k  - comment out a line in the buffer
u  - Uncomment a line in the buffer

b  - add Unicode BOM to the beginning of the file
B  - remove unicode BOM from the beginning of the file
S  - Split from line number to end of file into a new file
h  - print this Help message

w  - Write/Save buffer to file
q  - Quit the editor without saving changes
qq - force Quit without saving changes
x  - eXit the editor saving changes to file
```
