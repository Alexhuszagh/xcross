#!/bin/bash
# Run all tests.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/../images.sh"

for image in "${OS_IMAGES[@]}"; do
    ./docker-run.sh helloworld "$image"
done

for image in "${METAL_IMAGES[@]}"; do
    ./docker-run.sh add "$image"
done
