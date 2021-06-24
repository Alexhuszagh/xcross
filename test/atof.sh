#!/bin/bash
#
# Run the cpp-atof test, for bare-metal toolchains.
# Slightly more complicated, since we test a simple
# C/C++ standard library linking against `atof`, which
# requires a C-runtime and an allocator.

set -e

if [ "$TOOLCHAIN" = "" ]; then
    TOOLCHAIN=static
fi
if [ "$TOOLCHAIN_FLAGS" = "" ]; then
    TOOLCHAIN_FLAGS="-static"
fi

git clone https://github.com/Alexhuszagh/cpp-atof.git
cd cpp-atof

# Test CMake.
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/$TOOLCHAIN.cmake \
    $CMAKE_FLAGS \
    -DCMAKE_C_FLAGS="$CFLAGS $FLAGS" \
    -DCMAKE_CXX_FLAGS="$CXXFLAGS $FLAGS"
cmake --build .

# Test Makefile.
cd ..
source /env/$TOOLCHAIN
CXXFLAGS="$CXXFLAGS $FLAGS" make

# Test symbolic links
c++ atof.cc $TOOLCHAIN_FLAGS $FLAGS

# Test peripherals.
if [ "$NO_PERIPHERALS" = "" ]; then
    cc-cpu-list > /dev/null 2>&1
    if which run > /dev/null 2>&1; then
        run-cpu-list > /dev/null 2>&1
    fi
    target-specs > /dev/null 2>&1
fi
