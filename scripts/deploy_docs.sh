#!/bin/bash

set -e

cd `dirname $0`/..

poetry run mkdocs gh-deploy
