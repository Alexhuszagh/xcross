#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=sh4-linux-gnu
export VER=10
export ARCH=sh4
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run