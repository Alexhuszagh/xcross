#!/bin/bash
# Run a given test.

set -e

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
echo "$scriptdir"

cmd="$1"
image="$2"

docker run -v "$scriptdir:/test" \
    --env IMAGE="$image" \
    ahuszagh/cross:"$image" \
    /bin/bash -c "/test/$cmd.sh"
