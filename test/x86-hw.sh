#!/bin/bash
# Test a simple hello-world program for an x86 system.
#
# This requires a C standard library, a system allocator,
# stdio, and therefore tests reasonably well the hardware
# works.

set -e

cd /test/x86-hw
scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/common/shared.sh"
install x86
run
