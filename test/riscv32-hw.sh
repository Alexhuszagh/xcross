#!/bin/bash
# Test a simple hello-world program for a generic RISC-V 32-bit
# system.
#
# This requires a C standard library, a system allocator,
# stdio, and therefore tests reasonably well the hardware
# works.

set -e

cd /test/riscv32-hw
scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/common/shared.sh"
install riscv32
run
