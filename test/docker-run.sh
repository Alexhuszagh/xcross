#!/bin/bash
# Run a given test.

set -e

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
echo "$scriptdir"

command="/test/$1.sh"
image="$2"
if [ "$3" != "" ]; then
    command="export CPU=$3; $command"
fi

docker run -v "$scriptdir:/test" \
    --env IMAGE="$image" \
    --env CMAKE_FLAGS="$CMAKE_FLAGS" \
    --env FLAGS="$FLAGS" \
    ahuszagh/cross:"$image" \
    /bin/bash -c "$command"
