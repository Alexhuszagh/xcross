#!/bin/bash
#
# The first argument must be the arch, for building the Linux headers,
# and the 2nd argument must be the architecture triple.
#
# For example:
#   ARCH=powerpcle-unknown-elf ./gcc.sh

set -ex

export DEBIAN_FRONTEND="noninteractive"

# Install dependencies to build ct-ng.
# python3 is for glibc
# python3-pip for gdb
apt-get update
apt-get install --assume-yes --no-install-recommends \
    autoconf \
    bison \
    flex \
    g++ \
    gawk \
    help2man \
    libncurses-dev \
    libtool-bin \
    patch \
    python3 \
    python3-pip \
    texinfo \
    unzip \
    wget \
    xz-utils

# Create a source directory for easy cleanup.
mkdir -p src && cd src

# Build ct-ng
wget http://crosstool-ng.org/download/crosstool-ng/crosstool-ng-1.24.0.tar.xz
tar xvf crosstool-ng-1.24.0.tar.xz
cd crosstool-ng-1.24.0
./configure --prefix=/src/crosstoolng
make -j 5
make install

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
su crosstoolng -c "/src/crosstoolng/bin/ct-ng build.5"

# Cleanup
cd /
rm -rf src
apt-get remove --purge --assume-yes \
    autoconf \
    bison \
    flex \
    g++ \
    gawk \
    help2man \
    libncurses-dev \
    libtool-bin \
    patch \
    python3 \
    python3-pip \
    texinfo \
    unzip \
    wget \
    xz-utils
apt-get autoremove --assume-yes
