#!/bin/bash
# Test compiling a project with a zlib dependency installed via
# a package manager.

set -e

cd /test/zlib

# Only test conan if it's installed, which some build systems
# have issues with.
if which conan 2&> /dev/null; then
    # Test Meson with Conan
    rm -rf build
    mkdir -p build
    cd build
    conan install .. --build
    meson ..
    conan build ..
    cd ..

    # Test CMake with Conan
    rm -rf build
    mkdir -p build
    cd build
    conan install .. --build
    cmake ..
    cmake --build .
    cd ..
fi

# Test CMake with vcpkg
rm -rf build
mkdir -p build
cd build
cmake ..
cmake --build .
