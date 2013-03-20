PYTHON_FILES = $(shell grep '.py' setup.py | grep -v 'bin/env' | cut -f 2 -d "'")
PYTHON_NAMESPACES = $(shell grep '.py' setup.py | grep -v 'bin/env' | cut -f 2 -d "'" | sed 's@/__init__.py@@' | sed 's@.py@@' | sed 's@/@.@g' | cut -c 5-)

all:

install:
	rm -rf build
	rm -rf /usr/local/share/mfgames-font
	python setup.py install

clean:
	find -name "*.pyc" -o -name "*~" -print0 | xargs -0 rm -f

check:
	PYTHONPATH=src pylint \
		--reports=no \
		--include-ids=yes \
		--disable=R0904,C0103,R0902,R0201,R0903,R0915,R0914,R0801 \
		$(shell find src -name "*.py")

	cd test && PYTHONPATH=../src ./run_tests.py
