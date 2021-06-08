#!/bin/bash
# Scripts to automatically build and publish new versions.

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
cd "$scriptdir"

# Run python scripts to clean, configure, build, and publish xcross.
python3 setup.py clean
python3 setup.py configure
python3 setup.py build
python setup.py sdist bdist_wheel

# Can now add in the version here, previously, it might have been too old.
source "$scriptdir/docker/version.sh"

# Need to tag releases. First delete the tag if it's already been used.
git tag -d v"$VERSION"
git tag v"$VERSION"
git push --force --tags
