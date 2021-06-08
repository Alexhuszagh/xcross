#!/bin/bash
#
# Run the cpp-add test, for bare-metal toolchains.
# Not all toolchains support shared linking, so only
# use static linking.

set -e

git clone https://github.com/Alexhuszagh/cpp-add.git
cd cpp-add

# Test CMake.
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/static.cmake -DCMAKE_CXX_FLAGS="$FLAGS"
make

# Test Makefile.
cd ..
source /env/static
CXXFLAGS="$FLAGS" make

# Test symbolic links
c++ add.cc -static $FLAGS
