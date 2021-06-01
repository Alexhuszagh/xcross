#!/bin/bash
# Push all the docker images to DockerHub.

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
    docker push "ahuszagh/cross:$image"
    docker push "ahuszagh/cross:$image"-"$VERSION"
    if [[ "$image" == *-unknown-linux-gnu ]]; then
        base="${image%-unknown-linux-gnu}"
        docker push "ahuszagh/cross:$base"
        docker push "ahuszagh/cross:$base"-"$VERSION"
    fi
done
