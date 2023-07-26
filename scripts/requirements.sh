#!/bin/bash

set -e

if [[ "$1" != "--check" && "$1" != "--update" ]]; then
    echo "Run as '$0 --check' or '$0 --update'"
    exit 1
fi

ROOT=`dirname "$0"`/..
ROOT=`realpath "$ROOT"`
TEMP=`mktemp -d -t interlab-requirements-XXXXXXXX`
echo "### Interlab root dir $ROOT"
echo "### Using temp dir $TEMP"
cd "$TEMP"

echo
echo "### Running poetry version:"
poetry --version
echo "### Note: Github CI is using Poetry version:"
grep 'key: "\?poetry-[0-9\.]\+"\?$' "$ROOT/.github/workflows/test.yaml"

# Update default (full) requirements
echo
echo "### Writing standard requirements.txt"
cp "$ROOT/pyproject.toml" "$ROOT/poetry.lock" .
poetry lock --check
poetry export -o "requirements.txt" --without-hashes --without-urls

# Update requirements for google colab
echo
echo "### Writing tweaked requirements.txt for google colab"
# First, remove the "notebooks" group
sed 'H;1h;$!d;x;s/\[tool.poetry.group.notebooks.dependencies\][^[]*//' -i pyproject.toml
# google-colab specific versions
poetry add --lock "requests==2.27.1" "numpy==1.22.4" "decorator==4.4.2"
poetry export -o "requirements-colab.txt" --without dev --without-hashes --without-urls

echo
if [ "$1" == "--check" ]; then
    echo "### Checking requirement files being up-to-date ..."
    diff "$ROOT/requirements.txt" ./requirements.txt
    diff "$ROOT/requirements-colab.txt" ./requirements-colab.txt
else
    echo "### Updating requirement files in $ROOT ..."
    cp ./requirements.txt ./requirements-colab.txt "$ROOT"
fi

echo "### Finished, cleaning up"
cd "$ROOT"
rm -r "$TEMP"