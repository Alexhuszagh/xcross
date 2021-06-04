#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=xtensa-unknown-linux-uclibc
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/
export ARCH=xtensa
export LIBPATH="$DIR$PREFIX"/sysroot

shortcut_gcc
shortcut_util
shortcut_run
