#!/bin/bash
# Scripts to automatically tag new versions.

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
cd "$scriptdir"

# Can now add in the version here, previously, it might have been too old.
source "$scriptdir/docker/version.sh"

# Need to tag releases. First delete the tag if it's already been used.
git tag -d v"$VERSION"
git tag v"$VERSION"
