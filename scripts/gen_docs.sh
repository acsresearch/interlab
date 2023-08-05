#!/bin/bash

set -e

DIRS="interlab interlab_zoo"
DEST=docs

cd `dirname $0`/..

poetry run pdoc $DIRS -o $DEST --no-include-undocumented
