#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=nios2-unknown-linux-gnu
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/
export ARCH=nios2
export LIBPATH="$DIR$PREFIX"/sysroot

shortcut_gcc
shortcut_util
shortcut_run
