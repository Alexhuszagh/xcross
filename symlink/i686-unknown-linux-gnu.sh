#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=i686-linux-gnu
export VER=10
export ARCH=i386
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
