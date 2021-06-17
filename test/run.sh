#!/bin/bash
# Run all tests.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/../docker/images.sh"

has_started=yes
has_stopped=no
if [ "$START" != "" ]; then
    has_started=no
fi

# Generic tests
for image in "${OS_IMAGES[@]}"; do
    if [ "$has_started" = yes ] || [ "$START" = "$image" ]; then
        has_started=yes
        "$scriptdir/docker-run.sh" helloworld "$image"
    fi

    if [ "$STOP" = "$image" ]; then
        has_stopped=yes
        break
    fi
done

for image in "${METAL_IMAGES[@]}"; do
    if [ "$has_stopped" = yes ]; then
        break
    elif [ "$has_started" = yes ] || [ "$START" = "$image" ]; then
        has_started=yes
        FLAGS="-nostartfiles" "$scriptdir/docker-run.sh" atoi "$image"
    fi

    if [ "$STOP" = "$image" ]; then
        has_stopped=yes
        break
    fi
done

# Extensive custom OS tests.
if [ "$METAL_TESTS" != "" ]; then
    "$scriptdir/docker-run.sh" ppc_metal "ppc-unknown-elf"
fi

# Specific hardware examples.
"$scriptdir/docker-run.sh" helloworld ppc-unknown-linux-gnu e500mc
"$scriptdir/docker-run.sh" helloworld ppc64-unknown-linux-gnu power9
"$scriptdir/docker-run.sh" helloworld mips-unknown-linux-gnu 24Kf
