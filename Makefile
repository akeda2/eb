# eb.py Makefile
# 

all: stui del
# readme

# Create s-tui executable
stui:
	pyinstaller eb.py -F
	mv dist/eb .

# Remove files created by pyinstaller
del:
	rm -rf ./dist/ ./build/ ./*.spec ./*.pyc ./*.log eb.spec dist/

# Clear pyinstall cache and delete file
clean:
	pyinstaller --clean eb.py
	rm -rf ./dist/ ./build/ ./*.spec ./*.pyc ./*.log eb.spec dist/
