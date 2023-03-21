# eb.py Makefile
# 

all: eb del
# readme

# Create s-tui executable
eb:
	pyinstaller eb.py -F
	mv dist/eb .

# Remove files created by pyinstaller
del:
	rm -rf ./dist/ ./build/ ./*.spec ./*.pyc ./*.log eb.spec dist/

# Clear pyinstall cache and delete file
clean:
	pyinstaller --clean eb.py
	rm -rf ./dist/ ./build/ ./*.spec ./*.pyc ./*.log eb.spec dist/

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin

install:
	mkdir -p $(DESTDIR)$(BINDIR)
	install -m755 eb $(DESTDIR)$(BINDIR)/eb
