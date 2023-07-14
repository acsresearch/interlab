
set -e

cd `dirname $0`/..

# Format Python code
poetry run isort --profile black tests interlab
poetry run black tests interlab

# Lint Python code
poetry run flake8 tests interlab