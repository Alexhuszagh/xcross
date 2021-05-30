#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/exec.sh"

prefix=powerpcle-unknown-linux-gnu
dir=/home/crosstoolng/x-tools/"$prefix"/

exec "$dir"/bin/"$prefix"-gcc "/usr/bin/gcc" "/usr/bin/cc"
exec "$dir"/bin/"$prefix"-g++ "/usr/bin/g++" "/usr/bin/c++"
exec "$dir"/bin/"$prefix"-ar "/usr/bin/ar"
exec "$dir"/bin/"$prefix"-as "/usr/bin/as"
exec "$dir"/bin/"$prefix"-ranlib "/usr/bin/ranlib"
exec "$dir"/bin/"$prefix"-ld "/usr/bin/ld"
exec "$dir"/bin/"$prefix"-nm "/usr/bin/nm"
exec "$dir"/bin/"$prefix"-size "/usr/bin/size"
exec "$dir"/bin/"$prefix"-strings "/usr/bin/strings"
exec "$dir"/bin/"$prefix"-strip "/usr/bin/strip"
