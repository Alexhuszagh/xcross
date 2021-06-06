#!/bin/bash
# Run all tests.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/../docker/images.sh"

# Generic tests
for image in "${OS_IMAGES[@]}"; do
    "$scriptdir/docker-run.sh" helloworld "$image"
done

for image in "${METAL_IMAGES[@]}"; do
    "$scriptdir/docker-run.sh" add "$image"
done

# Extensive custom OS tests.
if [ "$METAL_TESTS" != "" ]; then
    "$scriptdir/docker-run.sh" ppc_metal "ppc-unknown-elf"
fi

# Specific hardware examples.
"$scriptdir/docker-run.sh" helloworld ppc-unknown-linux-gnu e500mc
"$scriptdir/docker-run.sh" helloworld ppc64-unknown-linux-gnu power9
"$scriptdir/docker-run.sh" helloworld mips-unknown-linux-gnu 24Kf
