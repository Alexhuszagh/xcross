#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=microblaze-xilinx-linux-gnu
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/
export ARCH=microblaze
export LIBPATH="$DIR$PREFIX"/sysroot

shortcut_gcc
shortcut_util
shortcut_run
