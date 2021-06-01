#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=x86_64-multilib-linux-musl
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/
export ARCH=i386
export LIBPATH="$DIR$PREFIX"/sysroot

CFLAGS="-m32" shortcut_gcc
shortcut_util
shortcut_run
