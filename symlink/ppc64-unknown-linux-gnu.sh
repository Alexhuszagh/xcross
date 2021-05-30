#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=powerpc64-linux-gnu
export VER=10
export ARCH=ppc64
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
