#!/bin/bash
#
# Pre-built android NDK.

export DEBIAN_FRONTEND="noninteractive"

# Install dependencies.
apt-get update
apt-get install --assume-yes --no-install-recommends \
    wget \
    unzip

# Create a source directory for easy cleanup.
mkdir -p src && cd src

# Extract pre-built Android SDK.
version=r22b
wget https://dl.google.com/android/repository/android-ndk-"$version"-linux-x86_64.zip
unzip android-ndk-"$version"-linux-x86_64.zip
rm android-ndk-"$version"-linux-x86_64.zip
mkdir -p /usr/local/toolchains
cp -r android-ndk-"$version"/toolchains/llvm /usr/local/toolchains

# Cleanup
cd /
rm -rf /src
apt-get remove --purge --assume-yes \
    wget \
    unzip
apt-get autoremove --assume-yes
