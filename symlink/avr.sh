#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=avr
export DIR=/home/crosstoolng/x-tools/"$prefix"/

shortcut_gcc
shortcut_util