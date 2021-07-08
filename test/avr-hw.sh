#!/bin/bash
# Test a simple hello-world program for an AVR microcontroller.
#
# This requires a C standard library, a system allocator,
# stdio, and therefore tests reasonably well the hardware
# works.

set -e

cd /test/avr-hw
scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/common/shared.sh"
install avr
run
