#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=alpha-linux-gnu
export VER=10
export ARCH=alpha
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
