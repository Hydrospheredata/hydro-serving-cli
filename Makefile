PYTHON=python

wheel:
	$(PYTHON) setup.py bdist_wheel

test: test-cli test-http

test-cli:
	export LC_ALL=en_us.UTF-8
	export LANG=en_us.UTF-8
	$(PYTHON) tests/cli_case.py

test-http:
	$(PYTHON) tests/http_client_tests.py