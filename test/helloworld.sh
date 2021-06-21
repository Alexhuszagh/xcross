#!/bin/bash
# Run the cpp-helloworld test, for toolchains built on an OS.

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

git clone https://github.com/Alexhuszagh/cpp-helloworld.git
cd cpp-helloworld

# Check our run conditions.
has_run=no
if command -v run &> /dev/null; then
    has_run=yes
fi
is_android=no
if [[ "$IMAGE" = *-android ]] || [[ "$IMAGE" = *-androideabi ]]; then
    is_android=yes
fi
is_armeb=no
if [[ "$IMAGE" = armeb-* ]] || [[ "$IMAGE" = arm64eb-* ]] || [[ "$IMAGE" = thumbeb-* ]]; then
    is_armeb=yes
fi
is_ppc32=no
if [[ "$IMAGE" = ppc-* ]]; then
    is_ppc32=yes
fi
is_microblaze=no
if [[ "$IMAGE" = microblaze* ]]; then
    is_microblaze=yes
fi
is_sh4be=no
if [[ "$IMAGE" = sh4be-* ]]; then
    is_sh4be=yes
fi
run_toolchain2=no
if [ "$has_run" = yes ] && [ "$is_ppc32" = no ] && [ "$is_microblaze" = no ]; then
    run_toolchain2=yes
fi
run_toolchain1=no
if [ "$has_run" = yes ] && [ "$is_android" = no ] && [ "$is_armeb" = no ] && [ "$is_sh4be" = no ]; then
    run_toolchain1=yes
fi
if [[ "$IMAGE" = xtensa* ]]; then
    # Bug with Xtensa where Qemu cannot properly emulate it,
    # even with valid instructions.
    run_toolchain1=no
    run_toolchain2=no
fi

# Test CMake.
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/$TOOLCHAIN1.cmake \
    $CMAKE_FLAGS \
    -DCMAKE_C_FLAGS="$CFLAGS $FLAGS" \
    -DCMAKE_CXX_FLAGS="$CXXFLAGS $FLAGS"
cmake --build .
if [ "$run_toolchain1" = yes ]; then
    cmake --build . -- run
    run hello
fi

rm -rf ./*
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/$TOOLCHAIN2.cmake \
    $CMAKE_FLAGS \
    -DCMAKE_C_FLAGS="$CFLAGS $FLAGS" \
    -DCMAKE_CXX_FLAGS="$CXXFLAGS $FLAGS"
cmake --build .
if [ "$run_toolchain2" = yes ]; then
    cmake --build . -- run
    run hello
fi

# Test Makefile.
cd ..
source /env/$TOOLCHAIN1
CXXFLAGS="$CXXFLAGS $FLAGS" make
if [ "$run_toolchain1" = yes ]; then
    run helloworld
fi

make clean
source /env/$TOOLCHAIN2
CXXFLAGS="$CXXFLAGS $FLAGS" make
if [ "$run_toolchain2" = yes ]; then
    run helloworld
fi

# Test symbolic links
c++ helloworld.cc $TOOLCHAIN1_FLAGS -o hello $FLAGS
if [ "$run_toolchain1" = yes ]; then
    run hello
fi

c++ helloworld.cc $TOOLCHAIN2_FLAGS -o hello $FLAGS
if [ "$run_toolchain2" = yes ]; then
    run hello
fi
