#!/bin/bash
# Run all tests.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/../docker/images.sh"

for image in "${OS_IMAGES[@]}"; do
    "$scriptdir/docker-run.sh" helloworld "$image"
done

for image in "${METAL_IMAGES[@]}"; do
    "$scriptdir/docker-run.sh" add "$image"
done

if [ "$METAL_TESTS" != "" ]; then
    "$scriptdir/docker-run.sh" ppc_metal "ppc-unknown-elf"
fi
