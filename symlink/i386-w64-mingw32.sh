#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=x86_64-w64-mingw32
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/

CFLAGS="-m32" shortcut_gcc
shortcut_util
