#!/bin/bash
# Scripts to automatically build new versions.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
cd "$scriptdir"

# Build the docker images.
"$scriptdir/docker/build.sh"

# Run python scripts to clean, configure, build, and publish xcross.
python3 setup.py clean
python3 setup.py configure
python3 setup.py build
python3 setup.py sdist bdist_wheel
