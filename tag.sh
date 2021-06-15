#!/bin/bash
# Scripts to automatically tag new versions.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
cd "$scriptdir"

# Can now add in the version here, previously, it might have been too old.
source "$scriptdir/docker/version.sh"

# Need to tag releases. First delete the tag if it's already been used.
tag=v"$VERSION"
if GIT_DIR="$scriptdir/.git" git rev-parse "$tag" >/dev/null 2>&1; then
    git tag -d "$tag"
fi
git tag "$tag"
