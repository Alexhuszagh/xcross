#!/bin/bash
# Build all the docker images.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/images.sh"
source "$scriptdir/version.sh"

images=(
    "base"
    "qemu"
    "${IMAGES[@]}"
)

for image in "${images[@]}"; do
    docker build -t "ahuszagh/cross:$image" "$scriptdir"/.. --file "$scriptdir/Dockerfile.$image"
    docker tag "ahuszagh/cross:$image" "ahuszagh/cross:$image"-"$VERSION"
    if [[ "$image" == *-unknown-linux-gnu ]]; then
        base="${image%-unknown-linux-gnu}"
        docker tag "ahuszagh/cross:$image" "ahuszagh/cross:$base"
        docker tag "ahuszagh/cross:$image" "ahuszagh/cross:$base"-"$VERSION"
    fi
done
