#!/bin/bash

set -e

cd `dirname $0`/..

#poetry run mkdocs gh-deploy
echo "For now, run 'mike deploy' manually *after* running 'scripts/gen_doc.sh'"
echo "- 'poetry run mike deploy -u -p latest' for latest docs ('main' branch)"
echo "- 'poetry run mike deploy -u -p --no-redirect 0.4.0 stable' for stable versions (replace 0.4.0)"
echo 
echo "NB: nothing was done"
exit 1
