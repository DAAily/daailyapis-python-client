include .env

install: 
	python3 -m venv venv
	venv/bin/pip install -r tests/requirements.txt

test:
	venv/bin/python -m pytest

sample-1:
	venv/bin/python -m samples.get_entities_from_lucy

build:
	$(info NOTE: Keep in mind to increment the version when doing a new build)
	python3 -m build

publish:
	python3 -m twine upload --repository-url https://europe-west3-python.pkg.dev/one-data-project/daailyapis-python-client/ dist/* --skip-existing

