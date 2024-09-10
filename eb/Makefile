# eb.py Makefile
# 

all: eb del
# readme

# Create eb executable
eb:
	pyinstaller --clean eb.py -F --noupx
	mv dist/eb .

# Remove files created by pyinstaller
del:
	rm -rf ./dist/ ./build/ ./*.spec ./*.pyc ./*.log eb.spec dist/

# Clear pyinstall cache and delete file
clean:
	#pyinstaller --clean eb.py
	rm -rf ./dist/ ./build/ ./*.spec ./*.pyc ./*.log eb.spec dist/ eb ./venv

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin

install:
	mkdir -p $(DESTDIR)$(BINDIR)
	install -m755 eb $(DESTDIR)$(BINDIR)/eb
