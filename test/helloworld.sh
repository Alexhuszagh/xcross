#!/bin/bash
# Run the cpp-helloworld test, for toolchains built on an OS.

set -e

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
is_musl=no
if [[ "$IMAGE" = *-musl ]]; then
    is_musl=yes
fi
is_ppc32=no
if [[ "$IMAGE" = ppc-* ]]; then
    is_ppc32=yes
fi
is_armeb=no
if [[ "$IMAGE" = armeb-* ]] || [[ "$IMAGE" = arm64eb-* ]] || [[ "$IMAGE" = thumbeb-* ]]; then
    is_armeb=yes
fi
is_sh4be=no
if [[ "$IMAGE" = sh4be-* ]]; then
    is_sh4be=yes
fi
run_static=no
if [ $has_run = yes ] && [ $is_ppc32 = no ]; then
    run_static=yes
fi
run_shared=no
if [ $has_run = yes ] && [ $is_android = no ] && [ $is_musl = no ] && [ $is_armeb = no ] && [ $sh4be = no ]; then
    run_shared=yes
fi
if [[ "$IMAGE" = xtensa* ]]; then
    # Bug with Xtensa where Qemu cannot properly emulate it,
    # even with valid instructions.
    run_shared=no
    run_static=no
fi

# Test CMake.
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/shared.cmake
make
if [ $run_shared = yes ]; then
    make run
    run hello
fi

rm -rf ./*
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/static.cmake
make
if [ $run_static = yes ]; then
    make run
    run hello
fi

# Test Makefile.
cd ..
source /env/shared
make
if [ $run_shared = yes ]; then
    run helloworld
fi

make clean
source /env/static
make
if [ $run_static = yes ]; then
    run helloworld
fi

# Test symbolic links
c++ helloworld.cc -fPIC -o hello
if [ $run_shared = yes ]; then
    run hello
fi

c++ helloworld.cc -static -o hello
if [ $run_static = yes ]; then
    run hello
fi
