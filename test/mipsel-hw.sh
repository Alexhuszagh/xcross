#!/bin/bash
# Test a simple hello-world program for a 32-bit MIPSEL system.
#
# This requires a C standard library, a system allocator,
# stdio, and therefore tests reasonably well the hardware
# works.

set -e

cd /test/mipsel-hw
scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/common/shared.sh"
install mips
run
