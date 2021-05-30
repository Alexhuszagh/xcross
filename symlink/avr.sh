#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=avr
export DIR=/home/crosstoolng/x-tools/"$prefix"/

shortcut_gcc
shortcut_util
