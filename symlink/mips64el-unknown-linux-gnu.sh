#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=mips64el-linux-gnuabi64
export VER=10
export ARCH=mips64el
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
