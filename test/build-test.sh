#!/bin/bash
# Run the build tests, for toolchains built on an OS.

set -e

if [ "$TOOLCHAIN1" = "" ]; then
    TOOLCHAIN1=shared
fi
if [ "$TOOLCHAIN1_FLAGS" = "" ]; then
    TOOLCHAIN1_FLAGS="-fPIC"
fi
if [ "$TOOLCHAIN2" = "" ]; then
    TOOLCHAIN2=static
fi
if [ "$TOOLCHAIN2_FLAGS" = "" ]; then
    TOOLCHAIN2_FLAGS="-static"
fi

# Check which images we should run.
run_toolchain1=no
run_toolchain2=no
if command -v run &> /dev/null; then
    run_toolchain1=yes
    run_toolchain2=yes
    warnings="/opt/bin/warnings.json"
    if [ -f "$warnings" ] && command -v jq --version >/dev/null 2>&1; then
        qemu=$(cat "$warnings" | jq '.qemu')
        if [ "$qemu" != "null" ]; then
            warn1=$(echo "$qemu" | jq ".$TOOLCHAIN1")
            warn2=$(echo "$qemu" | jq ".$TOOLCHAIN2")
            if [ "$warn1" == "true" ]; then
                run_toolchain1=no
            fi
            if [ "$warn2" == "true" ]; then
                run_toolchain2=no
            fi
        fi
    fi
fi

# Test CMake.
# Only build toolchain 1 (shared) if we do not have a bare-metal image.
cd /test/buildtests
mkdir -p build-"$IMAGE"
cd build-"$IMAGE"
if [ "$TYPE" != "metal" ]; then
    rm -rf ./*
    cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/$TOOLCHAIN1.cmake \
        $CMAKE_FLAGS \
        -DCMAKE_C_FLAGS="$CFLAGS $FLAGS $TOOLCHAIN1_FLAGS" \
        -DCMAKE_CXX_FLAGS="$CXXFLAGS $FLAGS $TOOLCHAIN1_FLAGS"
    cmake --build .
    if [ "$run_toolchain1" = yes ]; then
        cmake --build . -- run
    fi
fi

# Always build toolchain 2 (static).
rm -rf ./*
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/$TOOLCHAIN2.cmake \
    $CMAKE_FLAGS \
    -DCMAKE_C_FLAGS="$CFLAGS $FLAGS $TOOLCHAIN2_FLAGS" \
    -DCMAKE_CXX_FLAGS="$CXXFLAGS $FLAGS $TOOLCHAIN2_FLAGS"
cmake --build .
if [ "$run_toolchain2" = yes ]; then
    cmake --build . -- run
fi

# Cleanup our out-of-source build.
cd ..
rm -rf build-"$IMAGE"

# Test Makefile. Do not run these, since we don't know the target name.
# Only build toolchain 1 (shared) if we do not have a bare-metal image.
if [ "$TYPE" != "metal" ]; then
    source /env/$TOOLCHAIN1
    CXXFLAGS="$CXXFLAGS $FLAGS $TOOLCHAIN1_FLAGS" make
    make clean
    rm -f *.wasm
fi

# Always build toolchain 2 (static).
source /env/$TOOLCHAIN2
CXXFLAGS="$CXXFLAGS $FLAGS $TOOLCHAIN2_FLAGS" make
make clean
rm -f *.wasm

# Test symbolic links.
# Only build toolchain 1 (shared) if we do not have a bare-metal image.
if [ "$TYPE" != "metal" ]; then
    c++ *.cc -o exe $FLAGS $TOOLCHAIN1_FLAGS
    if [ "$run_toolchain1" = yes ]; then
        run exe
    fi
    rm -f exe exe.o exe.js exe.wasm
fi

# Always build toolchain 2 (static).
c++ *.cc -o exe $FLAGS $TOOLCHAIN2_FLAGS
if [ "$run_toolchain2" = yes ]; then
    run exe
fi
rm -f exe exe.o exe.js exe.wasm

# Test peripherals.
if [ "$NO_PERIPHERALS" = "" ] && [ "$TYPE" != "script" ]; then
    cc-cpu-list > /dev/null 2>&1
    if which run > /dev/null 2>&1; then
        run-cpu-list > /dev/null 2>&1
    fi
    target-specs > /dev/null 2>&1
    target-specs-full > /dev/null 2>&1
fi
