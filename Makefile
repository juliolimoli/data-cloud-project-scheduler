install:
	pip3 install --upgrade pip &&\
		pip3 install -r requirements.txt

lint:
	pylint --disable=R,C src/app.py

test:
	pytest --cov=app tests/ --cov-report html
	 
format:
	black *.py

all: install lint test format