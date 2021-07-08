#!/bin/bash
# Test a simple hello-world program for the PPC CPU e500.
#
# This requires a C standard library, a system allocator,
# and therefore tests reasonably well the hardware works.

set -e

cd /test/ppc-hw
scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/common/shared.sh"
install ppc
run
