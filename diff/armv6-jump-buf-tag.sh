#!/bin/bash
# Apply the ARMv6 patch.

scriptdir=`realpath $(dirname "$BASH_SOURCE")`

file=".build/src/glibc-2.31/bits/types/struct___jmp_buf_tag.h"
cp "$scriptdir"/armv6-jump-buf-tag.h "$file"
