#!/bin/bash

set -e

DIRS="interlab interlab_zoo treetrace"
API_DEST=docs/api

cd `dirname $0`/..

poetry run pdoc $DIRS -o $API_DEST --no-include-undocumented
poetry run mkdocs build

