#!/bin/bash
#
# Install dependencies for building crosstoolsng.

set -ex

export DEBIAN_FRONTEND="noninteractive"

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
