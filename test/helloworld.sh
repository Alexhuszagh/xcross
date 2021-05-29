#!/bin/bash
# Run the cpp-helloworld test, for toolchains built on an OS.

git clone https://github.com/Alexhuszagh/cpp-helloworld.git
cd cpp-helloworld
mkdir build && cd build

cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/shared.cmake
make

rm -rf ./*
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/static.cmake
make

shopt -s expand_aliases
source /env/shared
c++ ../helloworld.cc

source /env/static
c++ ../helloworld.cc
