#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=powerpcle-unknown-eabi
export DIR=/home/crosstoolng/x-tools/"$PREFIX"

shortcut_gcc
shortcut_util
