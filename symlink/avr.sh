#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=avr
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/

shortcut_gcc
shortcut_util
