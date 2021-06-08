#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=riscv64-unknown-elf
export DIR="/opt/riscv"

CFLAGS="-march=rv32imac -mabi=ilp32" shortcut_gcc
shortcut_util
