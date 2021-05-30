#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=hppa-linux-gnu
export VER=10
export ARCH=hppa
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
