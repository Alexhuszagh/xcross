#!/bin/bash
# Test a simple hello-world program on bash.

set -e

git clone https://github.com/Alexhuszagh/ppc_hw
cd ppc_hw
make

export DEBIAN_FRONTEND="noninteractive"
apt-get install --assume-yes qemu-system-ppc

# Run our kernel program.
# Need to exit on a 0 status.
timeout 0.1 make run || [[ $? -eq 124 ]]
