#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=microblazeel-xilinx-linux-gnu
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/
export ARCH=microblazeel
export LIBPATH="$DIR$PREFIX"/sysroot

shortcut_gcc
shortcut_util
shortcut_run
