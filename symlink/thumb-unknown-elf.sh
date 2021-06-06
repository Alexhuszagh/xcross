#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=arm-unknown-eabi
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/

CFLAGS="-mthumb -nostartfiles" shortcut_gcc
shortcut_util
