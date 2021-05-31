#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=
export VER=10
export ARCH=x86_64

shortcut_gcc
shortcut_run
