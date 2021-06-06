#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=armeb-unknown-linux-gnueabi
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/
export ARCH=armeb
export LIBPATH="$DIR$PREFIX"/sysroot

CFLAGS='-mthumb' shortcut_gcc
shortcut_util
shortcut_run
