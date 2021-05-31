#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=arm-linux-gnueabihf
export VER=10
export ARCH=arm
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
