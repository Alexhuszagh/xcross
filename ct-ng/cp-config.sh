#!/bin/bash
#
# Copy config files over.

set -ex

if [ "$ARCH" = "" ]; then
    echo 'Must set the host architecture via `$ARCH`, quitting.'
    exit 1
fi

# Toolchains can be built using:
#   ct-ng menuconfig
#
# Make sure to set under "Target options":
#   Target Architecture
#   ABI
#   Bitness
#   Endianness
#
# Make sure to set under "Toolchain Options":
#   Build Static Toolchain
#
# Make sure to set under "Operating System":
#   Target OS
#
# Make sure to set under "C compiler":
#   C++
#
# The config then needs to be patched to set:
#   CT_GCC_V_10=y
#   # CT_GCC_V_9 is not set
#   CT_GCC_VERSION="10.2.0"
#
# If using GLIBC, then we need to patch the config to set:
#   CT_GLIBC_V_2_31=y
#   # CT_GLIBC_V_2_30 is not set
#   # CT_GLIBC_V_2_29 is not set
#   CT_GLIBC_VERSION="2.31"

# Build our toolchain.
# When debugging, use `CT_DEBUG_CT_SAVE_STEPS=1 ct-ng build`
# so the build can restart. Find the offending step via
# `ct-ng list-steps`, and then restart via
# `RESTART=$step ct-ng build`. This dramatically speeds up
# debugging new builds.
cd /src
mkdir ct-ng-build
chown -R crosstoolng:crosstoolng ct-ng-build
cd ct-ng-build
cp /ct-ng/"$ARCH".config .config
chown crosstoolng:crosstoolng .config
