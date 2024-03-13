#!/bin/bash

# Formats and lints files in-place, or just checks them for formatting

DIRS="tests interlab interlab_zoo"

set -e

if [[ "$1" != "--check" && "x$1" != "x" ]]; then
    echo "Run as '$0 --check' or just '$0'"
    exit 1
fi

cd `dirname $0`/..

if [[ "$1" == "--check" ]]; then
    poetry run ruff format --check $DIRS
    poetry run ruff check $DIRS
    # Lint Python code
    # By default, this is skipped in checking
    #poetry run flake8 tests interlab
    echo "All code checks completed successfully"
else
    # Format Python code
    poetry run ruff format $DIRS

    # Lint Python code
    poetry run ruff check $DIRS

fi

