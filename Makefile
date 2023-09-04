
install: 
	python3 -m venv venv
	venv/bin/pip install -r tests/requirements.txt


test:

	venv/bin/python -m pytest -vv --cov=daaily --cov-report term-missing



local: 
	venv/bin/python main.py
	# venv/bin/pip install -r requirements.txt