#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=x86_64-linux-android
export DIR=/usr/local/toolchains/llvm/prebuilt/linux-x86_64

PREFIX=x86_64-linux-android30 shortcut_clang
shortcut_util
