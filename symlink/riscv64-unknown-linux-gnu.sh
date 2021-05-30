#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

prefix=riscv64-linux-gnu

exec "$prefix"-gcc-10 "/usr/bin/gcc" "/usr/bin/cc"
exec "$prefix"-g++-10 "/usr/bin/g++" "/usr/bin/c++"
exec "$prefix"-ar "/usr/bin/ar"
exec "$prefix"-as "/usr/bin/as"
exec "$prefix"-ranlib "/usr/bin/ranlib"
exec "$prefix"-ld "/usr/bin/ld"
exec "$prefix"-nm "/usr/bin/nm"
exec "$prefix"-size "/usr/bin/size"
exec "$prefix"-strings "/usr/bin/strings"
exec "$prefix"-strip "/usr/bin/strip"
