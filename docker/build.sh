#!/bin/bash
# Build all the docker images.

set -x

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

tag_semver() {
    local versions=($(semver))
    for version in "${versions[@]}"; do
        docker tag "$1" "$1"-"$version"
    done
}

failures=()
for image in "${images[@]}"; do
    if [ "$has_started" = yes ] || [ "$START" = "$image" ]; then
        has_started=yes
        username="ahuszagh"
        repository="cross"
        image_name="$username/$repository:$image"
        project_dir="$scriptdir"/..
        dockerfile="$scriptdir/images/Dockerfile.$image"
        docker build -t "$image_name" "$project_dir" --file "$dockerfile"
        if [ $? -eq 0 ]; then
            tag_semver "$image_name"
            if [[ "$image" == *-unknown-linux-gnu ]]; then
                base="${image%-unknown-linux-gnu}"
                base_image="$username/$repository:$base"
                docker tag "$image_name" "$base_image"
                tag_semver "$base_image"
            fi
        else
            failures+=("$image")
        fi

    fi

    if [ "$STOP" = "$image" ]; then
        break
    fi
done

if [ ${#failures[@]} -ne 0 ]; then
    echo "Error: Failures occurred."
    echo "-------------------------"
    for failure in "${failures[@]}"; do
        echo "$failure"
    done
fi
