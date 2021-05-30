#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=arm-linux-androideabi
export DIR=/usr/local/toolchains/llvm/prebuilt/linux-x86_64

PREFIX=armv7a-linux-androideabi30 shortcut_clang
shortcut_util
