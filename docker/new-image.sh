#!/bin/bash
# Create a new Docker image.
#
# Example:
#   BITNESS=32 OS=Linux TARGET=powerpcle-unknown-linux-gnu \
#       FILENAME=ppcle-unknown-linux-gnu ./new-image.sh

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`

if [ "$TARGET" = "" ]; then
    echo 'Must set the target triple via `$TARGET`, quitting.'
    exit 1
fi
arch=$(echo "$TARGET" | cut -d '-' -f 1)

if [ "$BITNESS" = "" ]; then
    echo 'Must set the architecture bitness `$BITNESS`, quitting.'
    exit 1
fi

if [ "$FILENAME" = "" ]; then
    # Sometimes the filename differs from the triple, such
    # as `ppcle-unknown-eabi` vs. `powerpcle-unknown-eabi`.
    FILENAME="$TARGET"
    base=$(echo "$FILENAME" | cut -d '-' -f 1)
fi

if [ "$OS" = "" ]; then
    OS="Generic"
fi

# Create our CMake toolchain file.
cmake="$scriptdir/cmake/$FILENAME.cmake"
if [ "$OS" = "Generic" ]; then
    echo "# Need to override the system name to allow CMake to configure,
# otherwise, we get errors on bare-metal systems.
SET(CMAKE_SYSTEM_NAME Generic)
SET(CMAKE_SYSTEM_PROCESSOR $arch)
CMAKE_POLICY(SET CMP0065 NEW)" > "$cmake"
else
    echo "SET(CMAKE_SYSTEM_NAME $OS)
SET(CMAKE_SYSTEM_PROCESSOR $arch)" > "$cmake"
fi
echo "set(ARCH $BITNESS)

SET(CMAKE_FIND_ROOT_PATH \"/home/crosstoolng/x-tools/$TARGET/\")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
" >> "$cmake"

# Create our symlink script.
env="$scriptdir/symlink/$FILENAME.sh"
echo '#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"
' > "$env"
echo "export PREFIX=$TARGET" >> "$env"
echo 'export DIR=/home/crosstoolng/x-tools/"$PREFIX"/

shortcut_gcc
shortcut_util'
