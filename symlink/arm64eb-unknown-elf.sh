#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=aarch64_be-unknown-elf
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/

shortcut_gcc
shortcut_util
