#!/bin/bash
# Run the cpp-add test, for bare-metal toolchains.

git clone https://github.com/Alexhuszagh/cpp-add.git
cd cpp-add
mkdir build && cd build

cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/shared.cmake
make

rm -rf ./*
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/static.cmake
make

shopt -s expand_aliases
source /env/shared
c++ ../add.cc

source /env/static
c++ ../add.cc
