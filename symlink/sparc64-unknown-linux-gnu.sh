#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=sparc64-linux-gnu
export VER=10
export ARCH=alpha
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
