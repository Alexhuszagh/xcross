#!/bin/bash
# Wrap a build test with cleanup to ensure.

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
"$scriptdir/build-test.sh"
code=$?

cd /test/buildtests
rm -rf build-"$IMAGE"
make clean
rm -f *.wasm
rm -f exe exe.o exe.js exe.wasm

exit $code
