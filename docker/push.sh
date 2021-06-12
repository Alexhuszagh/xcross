#!/bin/bash
# Push all the docker images to DockerHub.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/images.sh"
source "$scriptdir/version.sh"

images=(
    "base"
    "${IMAGES[@]}"
)

has_started=yes
if [ "$START" != "" ]; then
    has_started=no
fi

for image in "${images[@]}"; do
    if [ "$has_started" = yes ] || [ "$START" = "$image" ]; then
        has_started=yes
        docker push "ahuszagh/cross:$image"
        docker push "ahuszagh/cross:$image"-"$VERSION"
        if [[ "$image" == *-unknown-linux-gnu ]]; then
            base="${image%-unknown-linux-gnu}"
            docker push "ahuszagh/cross:$base"
            docker push "ahuszagh/cross:$base"-"$VERSION"
        fi
    fi

    if [ "$STOP" = "$image" ]; then
        break
    fi
done
