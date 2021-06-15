#!/bin/bash
# Build all the docker images.

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
        username="ahuszagh"
        repository="cross"
        image_name="$username/$repository:$image"
        project_dir="$scriptdir"/..
        dockerfile="$scriptdir/images/Dockerfile.$image"
        docker build -t "$image_name" "$project_dir" --file "$dockerfile"
        docker tag "$image_name" "$image_name"-"$VERSION"
        if [[ "$image" == *-unknown-linux-gnu ]]; then
            base="${image%-unknown-linux-gnu}"
            docker tag "$image_name" "$username/$repository:$base"
            docker tag "$image_name" "$username/$repository:$base"-"$VERSION"
        fi
    fi

    if [ "$STOP" = "$image" ]; then
        break
    fi
done
