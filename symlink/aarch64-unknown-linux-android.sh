#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=aarch64-linux-android
export DIR=/usr/local/toolchains/llvm/prebuilt/linux-x86_64

PREFIX=aarch64-linux-android30 shortcut_clang
shortcut_util
