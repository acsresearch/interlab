#!/bin/bash

# Formats and lints files in-place

set -e

cd `dirname $0`/..

# Format Python code
poetry run isort --profile black tests interlab interlab_zoo
poetry run black tests interlab interlab_zoo

# Lint Python code
poetry run flake8 tests interlab