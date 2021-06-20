#!/bin/bash
#
# Run the cpp-atof test, for bare-metal toolchains.
# Slightly more complicated, since we test a simple
# C/C++ standard library linking against `atof`, which
# requires a C-runtime and an allocator.

set -e

git clone https://github.com/Alexhuszagh/cpp-atof.git
cd cpp-atof

# Test CMake.
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/static.cmake \
    $CMAKE_FLAGS \
    -DCMAKE_C_FLAGS="$CFLAGS $FLAGS" \
    -DCMAKE_CXX_FLAGS="$CXXFLAGS $FLAGS"
cmake --build .

# Test Makefile.
cd ..
source /env/static
CXXFLAGS="$CXXFLAGS $FLAGS" make

# Test symbolic links
c++ atof.cc -static $FLAGS
