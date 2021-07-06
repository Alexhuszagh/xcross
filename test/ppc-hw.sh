#!/bin/bash
# Test a simple hello-world program for the PPC CPU e500.
#
# This requires a C standard library, a system allocator,
# and therefore tests reasonably well the hardware works.

set -e

cd /test/ppc-hw

export DEBIAN_FRONTEND="noninteractive"
apt-get update
apt-get install --assume-yes qemu-system-ppc

# Run our bare-metal image.
# Need to exit on a 0 status.
timeout 0.1 make run || [[ $? -eq 124 ]]
