include .env

install: 
	python3 -m venv venv
	venv/bin/pip install -r tests/requirements.txt

test:
	venv/bin/python -m pytest

sample-1:
	venv/bin/python -m samples.get_entities_from_lucy

local: 
	venv/bin/python main.py