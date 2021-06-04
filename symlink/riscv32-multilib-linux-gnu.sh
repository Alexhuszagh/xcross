#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=riscv64-unknown-linux-gnu
export DIR="/opt/riscv"
export ARCH=riscv32
export LIBPATH=("$DIR", "$DIR"/sysroot)

CFLAGS="-march=rv32imac -mabi=ilp32" shortcut_gcc
shortcut_util
shortcut_run
