#!/bin/bash

# Runs isort and black style checker, does not modify any files, exits with code 1 on error

set -e

cd `dirname $0`/..

# Format Python code
poetry run isort --check-only --profile black tests interlab
poetry run black --check tests interlab

# Lint Python code
# By default, this is skipped
#poetry run flake8 tests interlab

echo "All code checks completed successfully"
