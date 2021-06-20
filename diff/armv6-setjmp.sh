#!/bin/bash
# Apply the ARMv6 patch.

scriptdir=`realpath $(dirname "$BASH_SOURCE")`

file=".build/src/glibc-2.31/setjmp/setjmp.h"
patch "$file" "$scriptdir"/armv6-setjmp.diff
