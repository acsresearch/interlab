
set -e

cd `dirname $0`/..

# Format Python code
poetry run isort --profile black tests querychains
poetry run black tests querychains

# Lint Python code
poetry run flake8 tests querychains