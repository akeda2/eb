.PHONY: dev-setup test build

dev-setup:
	pip3 install -e . -r requirements-dev.txt

test:
	python3 -m unittest discover -s tests -v

build:
	./eb/build.sh
