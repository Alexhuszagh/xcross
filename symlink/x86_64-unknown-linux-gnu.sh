#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

exec /usr/bin/gcc-10 "/usr/bin/gcc" "/usr/bin/cc"
exec /usr/bin/g++-10 "/usr/bin/g++" "/usr/bin/c++"
