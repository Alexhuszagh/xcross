#!/bin/bash
# Run a given test.

set -e

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
echo "$scriptdir"

command="/test/image-test.sh"
if [ "$COMMAND" != "" ]; then
    command="/test/$COMMAND.sh"
fi
image="$1"
type="$2"
if [ "$3" != "" ]; then
    command="export CPU=$3; $command"
fi

docker run -v "$scriptdir:/test" \
    --env IMAGE="$image" \
    --env TYPE="$type" \
    --env CMAKE_FLAGS \
    --env TOOLCHAIN \
    --env TOOLCHAIN_FLAGS \
    --env TOOLCHAIN1 \
    --env TOOLCHAIN1_FLAGS \
    --env TOOLCHAIN2 \
    --env TOOLCHAIN2_FLAGS \
    --env NORUN1 \
    --env NORUN2 \
    --env FLAGS="$FLAGS" \
    ahuszagh/cross:"$image" \
    /bin/bash -c "$command"
