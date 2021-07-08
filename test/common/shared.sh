#!/bin/bash
# Shared functions for a bare-metal image test.

install() {
    export DEBIAN_FRONTEND="noninteractive"
    apt-get update
    apt-get install --assume-yes qemu-system-$1
}

run() {
    # Run our bare-metal image.
    # Need to exit on a 0 status.
    make
    timeout 0.1 make run || [[ $? -eq 124 ]]
    make clean
}
