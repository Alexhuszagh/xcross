#!/bin/bash
# Scripts to automatically build and publish new versions.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
cd "$scriptdir"

# Build and publish
"$scriptdir/build.sh"
"$scriptdir/tag.sh"

# Test and exit if anything fails
"$scriptdir/test/run.sh"

# Publish
"$scriptdir/docker/push.sh"
git push
git push --force --tags
twine upload dist/*
