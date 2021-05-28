# Toolchains

Simple C/C++ toolchains for cross-compiling, useful for testing cross-platform support, such as in CI pipelines. Images may be downloaded from [ahuszagh/cross](https://hub.docker.com/r/ahuszagh/cross)>

# Image Types

There are two types of images:
- Images with an OS layer, such as `ppcle-unknown-linux-gnu`.
- Bare metal images, such as `ppcle-unknown-elf`.

The bare metal images use the newlib C-runtime, and are useful for compiling for resource-constrained embedded systems, and by default do not link to any allocator.

The other images use a C-runtime that depends on a POSIX-like OS (such as Linux, FreeBSD, or MinGW for Windows), and can be used with:

- musl (`*-musl`)
- glibc (`*-gnu`)
- uclibc-ng (`*-uclibc`)
- android (`*-android`, only available on some architectures)

If you would like to test if the code compiles (and optionally, runs) for a target architecture, you should generally use a `linux-gnu` image.

**Triples**

All images are named as `ahuszagh/cross:$triple`, where `$triple` is the target triple. The target triple consists of:

- `arch`, the CPU architecture (mandatory).
- `vendor`, the CPU vendor.
- `os`, the OS the image is built on.
- `system`, the system type, which can comprise both the C-runtime and ABI.

For example, the following image names decompose to the following triples:

- `avr`, or `(avr, unknown, -, -)`
- `mips-unknown-o32`, `(mips, unknown, -, o32)`
- `mips-unknown-linux-gnu`, `(mips, unknown, linux, gnu)`

If an `$arch-unknown-linux-gnu` is available, then `$arch` is an alias for `$arch-unknown-linux-gnu`.

**Versioning**

Image names may optionally contain a trailing version, which will always use the same host OS, GCC, and C-runtime version.

- **No Version**: Alias for the latest version listed.
- **0.1**: GCC 10.2.0, glibc 2.31, and Ubuntu 20.04.

# Example

This runs through the logic of building and running a C++ project on PowerPC64, a big-endian system:

```bash
# Pull the Docker image, and run it interactively, entering the container.
image=alpha-unknown-linux-gnu
docker pull "ahuszagh/cross:$image"
docker run -it "ahuszagh/cross:$image" /bin/bash

# Clone the repository, build and run the code in the container using CMake.
git clone https://github.com/fastfloat/fast_float --depth 1
cd fast_float
mkdir build && cd build
cmake -DFASTFLOAT_TEST=ON -DCMAKE_TOOLCHAIN_FILE=/toolchains/ppc64-unknown-linux-gnu.cmake ..
make -j 2
qemu-ppc64 tests/basictest

# Use the toolchain environment varoables to build the project.
source /toolchains/env
cd /
git clone https://github.com/Alexhuszagh/cpp-helloworld.git
cd cpp-helloworld
$CXX helloworld.cc
```

# CI Example

A simple example of integrating cross images is as follows:

```yaml
language: cpp
dist: bionic
services:
  - docker

# Use a matrix with both native toolchains and cross-toolchain images.
matrix:
  include:
    - arch: amd64
      os: linux

    - arch: amd64
      os: linux
      env:
        - TOOLCHAIN="mips64"

before_install:
  - eval "${COMPILER}"
  - |
    if [ "$TOOLCHAIN" != "" ] ; then
      docker pull ahuszagh/cross:"$TOOLCHAIN"
    fi

script:
  - |
    if [ "$TOOLCHAIN" != "" ] ; then
      docker run -v "$(pwd)":/src ahuszagh/cross:"$TOOLCHAIN" /bin/bash \
        -c "cd src && ci/script.sh $TOOLCHAIN"
    else
      ci/script.sh
    fi
```

Where the contents of `script.sh` are as follows:

```bash
#!/bin/bash

TOOLCHAIN="$1"
# Configure and build the target.
mkdir build && cd build
if [ "$TOOLCHAIN" != "" ] ; then
    cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/"$TOOLCHAIN".cmake
else
    cmake ..
fi
make -j 5

# Use Qemu to test the target.
# Note that not all targets can be used with Qemu support.
if [ "$TOOLCHAIN" != "" ] ; then
  qemu-"$TOOLCHAIN" tests/test
else
    ctest --output-on-failure -R test
fi
```

# Building/Running Dockerfiles

To build all Docker images, run `build.sh`. To build and run a single docker image, use

```bash
image=ppcle-unknown-linux-gnu
docker build -t "ahuszagh/cross:$image" . --file "Dockerfile.$image"
docker run -it "ahuszagh/cross:$image" /bin/bash
```

# Requirements

In order to build the toolchains, you must have:

- Docker
- Bash
- Git
- Cut

Everything else runs in the container.

# Files

In order to use the cross-compiler toolchains, 2 files are provided:
- `/toolchains/*.cmake`, which is a toolchain file for use with CMake.
- `/toolchains/env`, which can be sourced to set `CC`, `CXX`, and other environment variables for other build systems.

# Developing New Toolchains

To add your own toolchain, the general workflow is as follows:

1. List toolchain samples.
2. Configure your toolchain.
3. Move the config file to `ct-ng`.
4. Patch the config file.
5. Create a source environment file.
6. Create a CMake toolchain file.
7. Create a `Dockerfile`.

After the toolchain is created, the source environment file, CMake toolchain file, and Dockerfile may be created via:

```bash
BITNESS=32 OS=Linux TARGET=arm-unknown-linux-gnueabi ./new-image.sh
```

**Configure Toolchain**

```bash
ct-ng list-samples
image=arm-unknown-linux-gnueabi
ct-ng "$image"
ct-ng menuconfig
mv .config ct-ng/"$image".config
ct-ng/patch.sh ct-ng/"$image".config
touch Dockerfile."$image"
```

**Source Environment File**

```bash
prefix=arm-unknown-linux-gnueabi
dir=/home/crosstoolng/x-tools/"$prefix"/
export CC="$dir"/bin/"$prefix"-gcc
export CXX="$dir"/bin/"$prefix"-g++
export AR="$dir"/bin/"$prefix"-ar
export AS="$dir"/bin/"$prefix"-as
export RANLIB="$dir"/bin/"$prefix"-ranlib
export LD="$dir"/bin/"$prefix"-ld
export NM="$dir"/bin/"$prefix"-nm
export SIZE="$dir"/bin/"$prefix"-size
export STRINGS="$dir"/bin/"$prefix"-strings
export STRIP="$dir"/bin/"$prefix"-strip
```

**CMake Toolchain File - Linux**

```cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR ppcle)

# COMPILERS
# ---------
SET(prefix powerpcle-unknown-linux-gnu)
SET(dir "/home/crosstoolng/x-tools/${prefix}")
SET(CMAKE_C_COMPILER "${dir}/bin/${prefix}-gcc")
SET(CMAKE_CXX_COMPILER "${dir}/bin/${prefix}-g++")
set(CMAKE_COMPILER_PREFIX "${prefix}-")

# PATHS
# -----
set(CMAKE_FIND_ROOT_PATH "${dir}/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# OTHER
# -----
set(ARCH 32)
SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static")
```

**CMake Toolchain File - Bare Metal**

```cmake
# Need to override the system name to allow CMake to configure,
# otherwise, we get errors on bare-metal systems.
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ppcle)
cmake_policy(SET CMP0065 NEW)

# COMPILERS
# ---------
SET(prefix powerpcle-unknown-elf)
SET(dir "/home/crosstoolng/x-tools/${prefix}")
SET(CMAKE_C_COMPILER "${dir}/bin/${prefix}-gcc")
SET(CMAKE_CXX_COMPILER "${dir}/bin/${prefix}-g++")
set(CMAKE_COMPILER_PREFIX "${prefix}-")

# PATHS
# -----
set(CMAKE_FIND_ROOT_PATH "${dir}/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# OTHER
# -----
set(ARCH 32)
SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static -Wl,--no-export-dynamic")
```

**Dockerfile**

```dockerfile
# Base image
FROM ahuszagh/cross:base

# Copy our config files and build GCC.
# This is done in a single step, so the docker image is much more
# compact, to avoid storing any layers with intermediate files.
COPY ct-ng/arm-unknown-linux-gnueabi.config /ct-ng/
COPY gcc.sh /ct-ng/
RUN ARCH=arm-unknown-linux-gnueabi /ct-ng/gcc.sh

# Remove GCC build scripts and config.
RUN rm -rf /ct-ng/

# Add toolchains
COPY cmake/arm-unknown-linux-gnueabi.cmake /toolchains
COPY cmake/arm-unknown-linux-gnueabi.cmake /toolchains/arm.cmake
COPY env/arm-unknown-linux-gnueabi /toolchains/env
```

For a bare-metal example, see `Dockerfile.ppcle-unknown-elf`. For a Linux example, see `Dockerfile.ppcle-unknown-linux-gnu`. Be sure to add your new toolchain to `images.sh`, and run the test suite with the new toolchain image.

# Pre-Built Images

For a list of pre-built images, see [DockerHub](https://hub.docker.com/r/ahuszagh/cross). To remove local, installed images from the pre-built, cross toolchains, run:

```bash
docker rmi $(docker images | grep 'ahuszagh/cross')
```

# Contributing

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in toolchains by you, will be unlicensed (free and unencumbered software released into the public domain).
