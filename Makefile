PYTHON=python

wheel:
	$(PYTHON) setup.py bdist_wheel

test:
	$(PYTHON) tests/tests.py