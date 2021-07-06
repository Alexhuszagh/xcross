#!/bin/bash
# Test a simple hello-world program for the ARM Versatile baseboard.
#
# This requires a C standard library, a system allocator,
# stdio, and therefore tests reasonably well the hardware
# works.

set -e

cd /test/arm-hw

export DEBIAN_FRONTEND="noninteractive"
apt-get update
apt-get install --assume-yes qemu-system-arm

# Run our bare-metal image.
# Need to exit on a 0 status.
timeout 0.1 make run || [[ $? -eq 124 ]]
