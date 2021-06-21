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

push_semver() {
    local versions=($(semver))
    docker push "$1"
    for version in "${versions[@]}"; do
        docker push "$image_name"-"$version"
    done
}

for image in "${images[@]}"; do
    if [ "$has_started" = yes ] || [ "$START" = "$image" ]; then
        has_started=yes
        push_semver "ahuszagh/cross:$image"
        if [[ "$image" == *-unknown-linux-gnu ]]; then
            base="${image%-unknown-linux-gnu}"
            push_semver "ahuszagh/cross:$base"
        fi
    fi

    if [ "$STOP" = "$image" ]; then
        break
    fi
done
