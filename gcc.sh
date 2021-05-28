#!/bin/bash
#
# Clean source files and dependencies.

set -ex

export DEBIAN_FRONTEND="noninteractive"

# Add non-root user to build libraries to.
adduser --disabled-password --gecos "" crosstoolng

# Install dependencies to build ct-ng.
# python3 is for glibc
# python3-pip and python3-dev for gdb
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
    python3-dev \
    python3-pip \
    texinfo \
    unzip \
    wget \
    xz-utils

# Create a source directory for easy cleanup.
mkdir -p src && cd src

# Build ct-ng
ctng_version=1.24.0
wget http://crosstool-ng.org/download/crosstool-ng/crosstool-ng-"$ctng_version".tar.xz
tar xvf crosstool-ng-"$ctng_version".tar.xz
cd crosstool-ng-"$ctng_version"
./configure --prefix=/src/crosstoolng
make -j 5
make install

# Copy config files over.
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

# Build up until we have the dependencies for the host.
cd /src/ct-ng-build
su crosstoolng -c "mkdir -p /home/crosstoolng/src"
su crosstoolng -c "CT_DEBUG_CT_SAVE_STEPS=1 /src/crosstoolng/bin/ct-ng build.5"

# Cleanup
cd /
rm -rf /src
rm -rf /home/crosstoolng/src
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
    python3-dev \
    python3-pip \
    texinfo \
    unzip \
    wget \
    xz-utils
apt-get autoremove --assume-yes
