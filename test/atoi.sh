#!/bin/bash
#
# Run the cpp-atoi test, for bare-metal toolchains.
# Slightly more complicated, since we test a simple
# C/C++ standard library linking against `atoi`
# which requires a C-runtime but no allocator.

set -e

if [ "$TOOLCHAIN" = "" ]; then
    TOOLCHAIN=static
fi
if [ "$TOOLCHAIN_FLAGS" = "" ]; then
    TOOLCHAIN_FLAGS="-static"
fi

git clone https://github.com/Alexhuszagh/cpp-atoi.git
cd cpp-atoi

# Test CMake.
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/$TOOLCHAIN.cmake \
    $CMAKE_FLAGS \
    -DCMAKE_C_FLAGS="$CFLAGS $FLAGS $TOOLCHAIN_FLAGS" \
    -DCMAKE_CXX_FLAGS="$CXXFLAGS $FLAGS $TOOLCHAIN_FLAGS"
cmake --build .

# Test Makefile.
cd ..
source /env/$TOOLCHAIN
CXXFLAGS="$CXXFLAGS $FLAGS $TOOLCHAIN_FLAGS" make

# Test symbolic links
c++ atoi.cc $TOOLCHAIN_FLAGS $FLAGS

# Test peripherals.
if [ "$NO_PERIPHERALS" = "" ]; then
    cc-cpu-list > /dev/null 2>&1
    if which run > /dev/null 2>&1; then
        run-cpu-list > /dev/null 2>&1
    fi
    target-specs > /dev/null 2>&1
fi
