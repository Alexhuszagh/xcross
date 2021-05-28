#!/bin/bash
#
# Build crosstoolsng.

set -ex

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
