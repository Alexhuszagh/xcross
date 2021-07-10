#!/bin/bash
# Test compiling a project with a zlib dependency installed via
# a package manager.

set -e

cd /test/zlib

# Test Meson with Conan
rm -rf build
mkdir -p build
cd build
conan install .. --build
meson ..
conan build ..

# Test CMake with Conan
cd ..
rm -rf build
mkdir -p build
cd build
conan install .. --build
cmake ..
cmake --build .

# Test CMake with vcpkg
cd ..
rm -rf build
mkdir -p build
cd build
cmake ..
cmake --build .
