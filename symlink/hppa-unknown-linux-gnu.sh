#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=hppa-linux-gnu
export VER=10
export ARCH=hppa
export LIBPATH="/usr/$PREFIX"
export HARDCODED="1.0"

shortcut_gcc
shortcut_util
shortcut_run
