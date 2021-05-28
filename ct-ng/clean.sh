#!/bin/bash
#
# Clean source files and dependencies.

set -ex

export DEBIAN_FRONTEND="noninteractive"

# Cleanup
cd /
rm -rf src
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
