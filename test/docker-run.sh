#!/bin/bash
# Run a given test.

CMD="$1"
IMAGE="$2"
TOOLCHAIN="$3"
if [ -z "$3" ]; then
    TOOLCHAIN="$IMAGE"
fi

docker run -v "$(pwd):/test" \
    ahuszagh/cross:"$IMAGE" \
    /bin/bash -c "/test/$CMD.sh $TOOLCHAIN"
