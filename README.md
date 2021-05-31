# Toolchains

Docker [images](https://hub.docker.com/r/ahuszagh/cross) and high-level scripts for plug-and-play C/C++ cross-compiling, inspired by [rust-embedded/cross](https://github.com/rust-embedded/cross). Toolchains supports both bare-metal and OS-based compilation, with a wide variety of architectures and C-runtimes supported. Toolchains is ideal for:

- Testing cross-platform support in CI pipelines.
- Building and deploying cross-compiled programs.

**Table of Contents**

- [Motivation](#motivation)
- [Getting Started](#getting-started)
    - [xcross](#xcross)
    - [run](#run)
    - [Docker](#docker)
- [Travis CI Example](#travis-ci-example)
- [Using xcross](#using-xcross)
- [Sharing Binaries To Host](#sharing-binaries-to-host)
- [Building/Running Dockerfiles](#building-running-dockerfiles)
- [Images](#images)
- [Development Dependencies](#development-dependencies)
- [Toolchain Files](#toolchain-files)
- [Developing New Toolchains](#developing-new-toolchains)
- [Platform Support](#platform-support)
- [License](#license)
- [Contributing](#contributing)

# Motivation

Unlike 10 years ago, we no longer live in an x86 world. ARM architectures are nearly ubiquitous in mobile devices, and popular in embedded devices, servers, and game systems. IBM's POWER and z/Architecture can run some high-end servers. PowerPC systems are popular in embedded devices, and used to be popular architectures for game systems, desktops, and servers. MIPS has been integral to autonomous driving systems and other embedded systems. RISC-V is rapidly being adopted for a wide variety of use-cases. The IoT market has lead to an explosion in embedded devices.

At the same time, modern software design builds upon a body of open source work. It is more important than ever to ensure that foundational libraries are portable, and can run on a wide variety of devices. However, few open source developers can afford a large selection of hardware to test code on, and most pre-packaged cross-compilers only support a few, common architectures.

Normally, cross compilers are limited by long compile times (to build the cross-compiler) and non-portable toolchain files, since the toolchain cannot be added to the path.

Using Docker images simplifies this, since the cross-compilers are pre-packaged in a compact image, enabling building, testing, and deploying cross-compiled code in seconds, rather than hours. Each image comes with a toolchain installed on-path, making it work with standard build tools without any configuration. And, [xcross](xcross) allows you to cross-compile code with zero setup required.

It just works.

# Getting Started

This shows a simple example of building and running a C++ project on PowerPC64, a big-endian system:

## xcross

xcross is a Python script to automate building transparently for custom targets, similar to Rust's [cross](https://github.com/rust-embedded/cross).

```bash
# Clone our project locally.
git clone https://github.com/Alexhuszagh/cpp-helloworld.git
cd cpp-helloworld

# Add xcross to any command, and it just works.
xcross make --target=alpha-unknown-linux-gnu
file helloworld
# helloworld: ELF 64-bit LSB executable, Alpha (unofficial)

# We can also use environment variables for the target and dir.
export TARGET=alpha-unknown-linux-gnu

# Let's try CMake. Here, we have to tell Docker where to 
# mount the directory, since we need to share the parent's files.
# Here we configure the project, build and run the executable.
mkdir build-alpha && cd build-alpha
xcross cmake ..
xcross make run
# Hello world!

# Let's try a raw C++ compiler. Here we build it using g++,
# and then run it using Qemu. It just works.
cd ..
xcross g++ helloworld.cc -o hello
xcross run hello

# We also support environment variable passthrough.
# Please note that if you use `$CXX`, it will evaluate
# on the host, so we must escape it.
xcross -E CXX=g++ '$CXX' helloworld.cc -o hello
```

## run

`run` is a command inside the docker image that invokes Qemu with the correct arguments to execute the binary, whether statically or dynamically-linked. `run hello` is analogous to running `./hello` as a native binary.

## Docker

For more fine-tuned control, you can also build a project within a container:

```bash
# Pull the Docker image, and run it interactively, entering the container.
image=alpha-unknown-linux-gnu
docker pull "ahuszagh/cross:$image"
docker run -it "ahuszagh/cross:$image" /bin/bash

# Clone the repository, build and run the code in the container using CMake.
# These toolchains in general aren't necessary, but ensure
# CMake knows we're cross-compiling and how to link.
git clone https://github.com/Alexhuszagh/cpp-helloworld.git
cd cpp-helloworld
mkdir build && cd build
# Build a statically-linked executable.
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/static.cmake
make
# Just works, as long as `add_custom_target` uses
# `${CMAKE_CROSSCOMPILING_EMULATOR} $<TARGET_FILE:..>`
# This uses Qemu as a wrapper, so running the executable
# only works on some architectures.
make run
# Can also run executables manually.
run hello

# Clean, and build a dynamically-linked executable.
rm -rf ./*
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/shared.cmake
make
# Just works, since `run` has the proper library search path.
make run
run hello

# Can also use Makefiles normally. Here we prefer shared linking,
# which also adds position-independent code. These environment
# only add the `-fPIC` or `-static` flags: nothing else is modified.
cd ..
source /toolchains/shared
make
run helloworld

# Can also use static linking.
source /toolchains/static
make clean
make
run helloworld

# Can also just raw `c++` and `cc` commands.
# It's really that simple.
c++ helloworld.cc -fPIC
run a.out

c++ helloworld.cc -static
run a.out
```

# Travis CI Example

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
        - TARGET="mips64"

before_install:
  - |
    if [ "$TARGET" != "" ] ; then
      wget https://raw.githubusercontent.com/Alexhuszagh/toolchains/main/bin/xcross
      chmod +x xcross
      docker pull ahuszagh/cross:"$TARGET"
    fi

script:
  - |
    mkdir build && cd build
    xcross=
    if [ "$TARGET" != "" ] ; then
      xcross=../xcross --target="$TARGET"
    fi
    $xcross cmake ..
    $xcross make -j 5
    $xcross run tests/test
```

# Using xcross

Most of the magic happens via xcross, which allows you to transparently execute commands in a Docker container. Although xcross provides simple, easy-to-use defaults, it has more configuration options for extensible cross-platform builds. Most of these command-line arguments may be provided as environment variables.

> **WARNING** By default, the root directory is shared with the Docker container, for maximum compatibility. In order to mitigate any security vulnerabilities, we run any build commands as a non-root user, and ensure all commands are properly escaped to avoid any script injections. If you are worried about a malicious build system, you may further restrict this using the `--dir` option.

### Installing

Install Python3.6+, then download [xcross](https://raw.githubusercontent.com/Alexhuszagh/toolchains/main/bin/xcross) and add it to the path. For example, on Unix systems:

```bash
# Download the file and make it executable.
wget https://raw.githubusercontent.com/Alexhuszagh/toolchains/main/bin/xcross \
    -P ~/bin
chmod +x ~/bin/xcross
# Add it to the path for the current and all future shells.
export PATH="$PATH:~/bin"
echo 'export PATH="$PATH:~/bin"' >> ~/.bashrc
```

### Arguments

- `--target`, `TARGET`: The target architecture to compile to.

```bash
# These two are identical, and build for Alpha on Linux/glibc
xcross --target=alpha-unknown-linux-gnu ...
TARGET=alpha-unknown-linux-gnu xcross ...
```

- `--dir`, `CROSS_DIR`: The target architecture to compile to.

```bash
# These two are identical, and share only from the 
# current working directory.
xcross --dir=. ...
CROSS_DIR=. xcross ...
```

- `-E`, `--env`: Pass environment variables to the container.

If no value is passed for the variable, it exports the variable from the current environment.

```bash
# These are all identical.
xcross -E VAR1 -E VAR2=x -E VAR3=y
xcross -E VAR1 -E VAR2=x,VAR3=y
xcross -E VAR1,VAR2=x,VAR3=y
```

- `--cpu`, `CROSS_CPU`: Set the CPU model to compile/run code for.

If not provided, it defaults to a generic processor model for the architecture. If provided, it will set the register usage and instruction scheduling parameters in addition to the generic processor model.

```bash
# Build for the PowerPC e500mc line.
export TARGET=ppc-unknown-linux-gnu
xcross --cpu=e500mc c++ helloworld.cc -o hello
xcross --cpu=e500mc run hello
```

In order to determine valid CPU model types for the cross-compiler, you may use either of the following commands:

```bash
# Check GCC for the valid CPU types, using an obviously false CPU type.
export TARGET=ppc-unknown-linux-gnu
xcross cc -mcpu=unknown
# error: unrecognized argument in option '-mcpu=unknown'
# gcc: note: valid arguments to '-mcpu=' are: 401 403...

# Check Qemu for known CPU types.
# The second column contains the desired data.
xcross run -cpu help
# PowerPC 601_v1           PVR 00010001
# PowerPC 601_v0           PVR 00010001
# ...
# PowerPC e500mc           PVR 80230020
# ...
```

- `--username`, `USERNAME`: The Docker Hub username for the Docker image.

This defaults to `ahuszagh` if not provided, however, it may be explicit set to an empty string. If the username is not empty, the image has the format `$username/$repository:$target`, otherwise, it has the format `$repository:$target`.

```bash
# These are all identical.
xcross --username=ahuszagh ...
USERNAME=ahuszagh xcross ...
```

- `--repository`, `REPOSITORY`: The name of the repository for the image.

This default to `cross` if not provided or is empty.

```bash
# These are all identical.
xcross --repository=cross ...
REPOSITORY=cross xcross ...
```

- `--docker`, `DOCKER`: The command for the Docker executable.

This default to `docker` if not provided or is empty.

```bash
# These are all identical.
xcross --docker=docker ...
DOCKER=docker xcross ...
```

# Sharing Binaries To Host

In order to build projects and share data back to the host machine, you can use Docker's `--volume` to bind a volume from the host to client. This allows us to share a build directory between the client and host, allowing us to build binaries with inside the container and test/deploy on the host.

```bash
# On a Linux distro with SELinux, you may need to turn it
# to permissive, to enable file sharing:
#   `setenforce 0`

# Run docker image, and share current directory.
image=alpha-unknown-linux-gnu
git clone https://github.com/Alexhuszagh/cpp-helloworld.git
docker run -it --volume "$(pwd)/cpp-helloworld:/hello" \
    "ahuszagh/cross:$image" \
    /bin/bash

# Enter the repository, and make a platform-specific build.
cd hello
mkdir build-alpha && cd build-alpha
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/static.cmake \
    -DCMAKE_BUILD_TYPE=Release
make

# Exit, and check we have our proper image.
exit
file cpp-helloworld/build-alpha/hello
# cpp-helloworld/build-alpha/hello: ELF 64-bit LSB executable, 
# Alpha (unofficial), version 1 (GNU/Linux), statically linked, 
# BuildID[sha1]=252707718fb090ed987a9eb9ab3a8c3f6ae93482, for 
# GNU/Linux 3.2.0, not stripped

# Please note the generated images will be owned by `root`.
ls -lh cpp-helloworld/build-alpha/hello
# -rwxr-xr-x. 1 root root 2.4M May 30 20:50 cpp-helloworld/build-alpha/hello
```

# Building/Running Dockerfiles

To build all Docker images, run `build.sh`. To build and run a single docker image, use

```bash
image=ppcle-unknown-linux-gnu
docker build -t "ahuszagh/cross:$image" . --file "Dockerfile.$image"
docker run -it "ahuszagh/cross:$image" /bin/bash
```

# Images

For a list of pre-built images, see [DockerHub](https://hub.docker.com/r/ahuszagh/cross). To remove local, installed images from the pre-built, cross toolchains, run:

```bash
docker rmi $(docker images | grep 'ahuszagh/cross')
```

**Image Types**

There are two types of images:
- Images with an OS layer, such as `ppcle-unknown-linux-gnu`.
- Bare metal images, such as `ppcle-unknown-elf`.

The bare metal images use the newlib C-runtime, and are useful for compiling for resource-constrained embedded systems, and do not link to a memory allocator.

The other images use a C-runtime that depends on a POSIX-like OS (such as Linux, FreeBSD, or MinGW for Windows), and can be used with:

- musl (`*-musl`)
- glibc (`*-gnu`)
- uClibc-ng (`*-uclibc`)
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

**OS Support**

In general, the focus of these images is to provide support for a wide variety of architectures, not operating systems. We will gladly accept Dockerfiles/scripts to support more operating systems, like FreeBSD.

We do not support Darwin/iOS for licensing reasons, since reproduction of the macOS SDK is expressly forbidden. If you would like to build a Darwin cross-compiler, see [osxcross](https://github.com/tpoechtrager/osxcross).

**Versioning**

Image names may optionally contain a trailing version, which will always use the same host OS, GCC, and C-runtime version.

- **No Version**: Alias for the latest version listed.
- **0.1**: GCC 10.2.0, glibc 2.31, and Ubuntu 20.04.

# Dependencies

In order to use `xcross`, you must have:

- python (3.6+)

In order to build the toolchains, you must have:

- docker
- bash

In order to add new toolchains, you must have:

- crosstool-NG
- cut

Everything else runs in the container.

# Toolchain Files

In order to simplify using the cross-compiler with CMake, we provide 3 CMake toolchain files:

- `/toolchains/toolchain.cmake`, which contains the necessary configurations to cross-compile.
- `/toolchains/shared.cmake`, for building dynamically-linked binaries.
- `/toolchains/static.cmake`, for building statically-linked binaries.

Likewise, to simplify using the cross-compiler with Makefiles, we provide 2 Bash config files:

- `/env/shared`, for building dynamically-linked binaries.
- `/env/static`, for building statically-linked binaries.

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
#!/bin/bash

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/shortcut.sh"

export PREFIX=arm-unknown-linux-gnueabi
export DIR=/home/crosstoolng/x-tools/"$PREFIX"/

shortcut_gcc
shortcut_util
```

**CMake Toolchain File - Linux**

```cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(CMAKE_FIND_ROOT_PATH "home/crosstoolng/x-tools/arm-unknown-linux-gnueabi/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

**CMake Toolchain File - Bare Metal**

```cmake
# Need to override the system name to allow CMake to configure,
# otherwise, we get errors on bare-metal systems.
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)
cmake_policy(SET CMP0065 NEW)

set(CMAKE_FIND_ROOT_PATH "/home/crosstoolng/x-tools/arm-unknown-eabi/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
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

 Add symlinks
COPY symlink/shortcut.sh /
COPY symlink/arm-unknown-linux-gnueabi.sh /
RUN /arm-unknown-linux-gnueabi.sh
RUN rm /shortcut.sh /arm-unknown-linux-gnueabi.sh

# Add toolchains
COPY cmake/arm-unknown-linux-gnueabi.cmake /toolchains/toolchain.cmake
COPY cmake/shared.cmake /toolchains/
COPY cmake/static.cmake /toolchains/
COPY env/shared /env/
COPY env/static /env/
```

For a bare-metal example, see `Dockerfile.ppcle-unknown-elf`. For a Linux example, see `Dockerfile.ppcle-unknown-linux-gnu`. Be sure to add your new toolchain to `images.sh`, and run the test suite with the new toolchain image.

# Platform Support

Currently, we only create images that are supported by:

- crosstool-NG with official sources
- Debian packages
- Android NDK's

We therefore support:

- ARM64 (Linux, Android)
- ARM32 (Linux, Android)
- Alpha (Linux)
- AVR (embedded)
- HPPA (Linux)
- i686 (Linux, MinGW, Android)
- M68K (Linux)
- MIPS (Linux, embedded)
- MIPS-LE (Linux, embedded)
- MIPS64 (Linux, embedded)
- MIPS64-LE (Linux, embedded)
- PowerPC (Linux, embedded)
- PowerPC-LE (Linux, embedded)
- PowerPC64 (Linux, embedded)
- PowerPC64-LE (Linux, embedded)
- Risc-V64 (Linux)
- S390x (Linux)
- SH1-4 (Linux, embedded)
- Sparc64 (Linux)
- x86_64 (Linux, MinGW, Android, embedded)

Platform-specific details:

- Xtensa does not support newlib, glibc, or musl.

# License

This is free and unencumbered software released into the public domain. This project, however, does derive off of projects that are not necessarily public domain software, such as [crosstool-NG](https://github.com/crosstool-ng/crosstool-ng), the [Android NDK](https://android.googlesource.com/platform/prebuilts/ndk/+/master/NOTICE), as well as build off of GCC, the Linux kernel headers, and the relevant C-runtime (glibc, musl, uClibc-ng).

These licenses are only relevant if you distribute a toolchain as part of a proprietary system: for merely compiling and linking code as part of a standard toolchain, the usual linking exceptions apply.

# Contributing

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in toolchains by you, will be unlicensed (free and unencumbered software released into the public domain).
