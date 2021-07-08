#!/bin/bash
# Test a simple hello-world program for the ARM Versatile baseboard.
#
# This requires a C standard library, a system allocator,
# stdio, and therefore tests reasonably well the hardware
# works.

set -e

cd /test/arm-hw
scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/common/shared.sh"
install aarch64
run
