test:
	pytest tests

fmt:
	black functions tests
	isort functions tests

lint:
	black --check functions tests
	isort --check-only functions tests
	flake8 functions tests
	mypy functions tests

pip_dev:
	pip install -r requirements_dev.txt -c requirements.lock

pip_prod:
	pip install -r requirements.txt -c requirements.lock
