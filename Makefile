PYTHON=python

wheel:
	$(PYTHON) setup.py bdist_wheel

test: lint
	export LC_ALL=en_us.UTF-8
	export LANG=en_us.UTF-8
	$(PYTHON) setup.py test

lint:
	pylint --rcfile=pylint.cfg hydroserving