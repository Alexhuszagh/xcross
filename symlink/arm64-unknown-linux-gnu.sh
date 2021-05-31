#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=aarch64-linux-gnu
export VER=10
export ARCH=aarch64
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
