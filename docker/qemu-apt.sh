#!/bin/bash
#
# Install Qemu from APT sources and remove unnecessary targets.
#   Ex: ARCH=riscv ./qemu-apt.sh
#
# A full qemu-user install is ~80MB, while a full qemu-user-static
# install is ~281MB, which is a lot compared to our image size.
# Remove all other targets.

set -ex

# Check required environment variables.
if [ "$ARCH" = "" ]; then
    echo "Invalid arch, must provide a valid architecture prefix."
    exit 1
fi

# Install qemu-user-static, and remove everything
# besides our desired architecture.
apt-get update
DEBIAN_FRONTEND="noninteractive" apt-get install --assume-yes --no-install-recommends \
    binfmt-support \
    qemu-user-static

# Remove all binaries.
# All other files are comically small.
bins=($(ls /usr/bin/qemu-* | grep qemu))
for bin in "${bins[@]}"; do
    if [ "$bin" != /usr/bin/qemu-"$ARCH"-static ]; then
        rm -f "$bin"
    else
        mv "$bin" /opt/bin
    fi
done
