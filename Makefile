.PHONY: build start test venv run clean env install-dependencies setup-project build

build:
	docker-compose build

start:
	docker-compose up

test:
	docker-compose run --rm app sh -c "python manage.py test && flake8"

# define the name of the virtual environment directory
VENV := venv

# venv is a shortcut target
venv: $(VENV)/bin/activate

run:
	$(VENV)/bin/python manage.py runserver

testlocal: venv
	.$(VENV)/bin/activate; pytest

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete

env:
	python3 -m venv $(VENV)

build: env install-dependencies setup-project
	echo "Build Completed!"

install-dependencies:
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

setup-project:
	$(VENV)/bin/python manage.py makemigrations
	$(VENV)/bin/python manage.py migrate
	$(VENV)/bin/python manage.py loaddata usagetypes.json
