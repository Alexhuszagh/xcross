#!/bin/bash
# Build all the docker images.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/images.sh"
source "$scriptdir/version.sh"

has_started=yes
if [ "$1" != "" ]; then
    has_started=no
    start="$1"
fi

images=(
    "base"
    "${IMAGES[@]}"
)

for image in "${images[@]}"; do
    if [ "$has_started" = yes ] || [ "$start" = "$image" ]; then
        has_started=yes
        docker build -t "ahuszagh/cross:$image" "$scriptdir"/.. --file "$scriptdir/Dockerfile.$image"
        docker tag "ahuszagh/cross:$image" "ahuszagh/cross:$image"-"$VERSION"
        if [[ "$image" == *-unknown-linux-gnu ]]; then
            base="${image%-unknown-linux-gnu}"
            docker tag "ahuszagh/cross:$image" "ahuszagh/cross:$base"
            docker tag "ahuszagh/cross:$image" "ahuszagh/cross:$base"-"$VERSION"
        fi
    fi
done
