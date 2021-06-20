#!/bin/bash
#
# Run the cpp-atoi test, for bare-metal toolchains.
# Slightly more complicated, since we test a simple
# C/C++ standard library linking against `atoi`
# which requires a C-runtime but no allocator.

set -e

git clone https://github.com/Alexhuszagh/cpp-atoi.git
cd cpp-atoi

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
c++ atoi.cc -static $FLAGS
