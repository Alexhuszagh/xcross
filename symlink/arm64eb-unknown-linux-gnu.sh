#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=aarch64_be-unknown-linux-gnu
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/
export ARCH=aarch64_be
export LIBPATH="$DIR$PREFIX"/sysroot

shortcut_gcc
shortcut_util
shortcut_run
