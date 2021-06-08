#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=sh-unknown-elf
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/

CFLAGS="-m3" shortcut_gcc
shortcut_util
