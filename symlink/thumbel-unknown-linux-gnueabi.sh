#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=arm-linux-gnueabi
export VER=10
export ARCH=arm
export LIBPATH="/usr/$PREFIX"

CFLAGS='-mthumb' shortcut_gcc
shortcut_util
shortcut_run
