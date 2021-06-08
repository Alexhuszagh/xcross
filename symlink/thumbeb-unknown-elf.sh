#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=armeb-unknown-eabi
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/

CFLAGS="-mthumb" shortcut_gcc
shortcut_util
