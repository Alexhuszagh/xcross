#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=s390x-linux-gnu
export VER=10
export ARCH=s390x
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
