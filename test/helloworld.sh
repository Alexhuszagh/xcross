#!/bin/bash
# Run the cpp-helloworld test, for toolchains built on an OS.

TOOLCHAIN="$1"
git clone https://github.com/Alexhuszagh/cpp-helloworld.git
cd cpp-helloworld
mkdir build && cd build

cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/"$TOOLCHAIN.cmake"
make

source /toolchains/env
$CXX ../helloworld.cc
