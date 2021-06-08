#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=mips64-unknown-elf
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/

CFLAGS="-mabi=32" shortcut_gcc
shortcut_util
