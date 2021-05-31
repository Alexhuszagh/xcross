#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=m68k-linux-gnu
export VER=10
export ARCH=m68k
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
