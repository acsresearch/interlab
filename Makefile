help:
	@echo "Targets:"
	@echo "  clean - remove all build, test, coverage and Python artifacts"
	@echo "  test - run tests quickly with the default Python"
	@echo "  format - format code with black and check it with flake8"
	@echo "  docs - generate documentation, including API docs"
	@echo "  docs_publish_latest - generate and publish documentation to 'gh-pages' as the 'latest' version"
	@echo "  check_requirements - check if requirements*.txt are up to date with poetry.lock"
	@echo "  update_requirements - update requirements*.txt to match poetry.lock"
	@echo "  lab - run Jupyter Lab server"
	
clean:
	rm -rf site docs/api .pytest_cache dist
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	@echo "\nRemaining untracked and ignored files:"
	git st --ignored --porcelain

test:
	poetry run pytest

format:
	scripts/format.sh

docs:
	script/gen_docs.sh

docs_publish_latest: docs
	poetry run mike deploy -u -p latest

check_requirements:
	scripts/requirements.sh --check

update_requirements:
	scripts/requirements.sh --update

lab:
	poetry run jupyter lab

.PHONY: help clean test docs docs_publish_latest check_requirements update_requirements lab
