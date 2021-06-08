#!/bin/bash
# Scripts to automatically build and publish new versions.

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
cd "$scriptdir"

# Build and publish
"$scriptdir/build.sh"
twine upload dist/*
