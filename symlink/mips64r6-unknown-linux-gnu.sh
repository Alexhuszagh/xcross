#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

export PREFIX=mipsisa64r6-linux-gnuabi64
export VER=10
export ARCH=mips64
export LIBPATH="/usr/$PREFIX"

shortcut_gcc
shortcut_util
shortcut_run
