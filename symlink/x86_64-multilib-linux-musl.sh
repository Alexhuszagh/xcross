#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=x86_64-multilib-linux-musl
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/
export ARCH=x86_64
export LIBPATH="$DIR$PREFIX"/sysroot

shortcut_gcc
shortcut_util
shortcut_run
