
install: 
	python3 -m venv venv

local: 
	venv/bin/python main.py
	# venv/bin/pip install -r requirements.txt