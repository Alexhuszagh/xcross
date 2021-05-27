#!/bin/bash
# Run the cpp-add test, for bare-metal toolchains.

TOOLCHAIN="$1"
git clone https://github.com/Alexhuszagh/cpp-add.git
cd cpp-add
mkdir build && cd build

cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/"$TOOLCHAIN.cmake"
make

source /toolchains/env
$CXX ../add.cc
