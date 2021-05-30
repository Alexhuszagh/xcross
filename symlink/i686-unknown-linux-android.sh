#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=i686-linux-android
export DIR=/usr/local/toolchains/llvm/prebuilt/linux-x86_64

PREFIX=i686-linux-android30 shortcut_clang
shortcut_util
