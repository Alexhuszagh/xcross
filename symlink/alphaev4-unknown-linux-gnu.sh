#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=alphaev4-unknown-linux-gnu
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/
export ARCH=alpha
export LIBPATH="$DIR$PREFIX"/sysroot

shortcut_gcc
shortcut_util
shortcut_run
