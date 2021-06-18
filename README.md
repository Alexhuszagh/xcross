# xcross

Compact docker [images](https://hub.docker.com/r/ahuszagh/cross) and high-level scripts for plug-and-play C/C++ cross-compiling, inspired by [rust-embedded/cross](https://github.com/rust-embedded/cross). xcross supports both bare-metal and OS-based compilation, with a wide variety of architectures and C-runtimes supported. xcross is ideal for:

- Testing cross-platform support in CI pipelines.
- Building and deploying cross-compiled programs.

Each Docker image comes pre-installed with:

- C and C++ cross compiler and standard library
- Autotools
- Binutils
- CMake
- Ninja

Note that this project is similar to [dockercross](https://github.com/dockcross/dockcross), however, xcross supports many more CPU architectures than dockcross. If you need Docker images of common architectures, dockcross should have better support.

**Table of Contents**

- [Motivation](#motivation)
- [Getting Started](#getting-started)
  - [Installing](#installing)
  - [xcross](#xcross)
  - [Build Tools](#build-tools)
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

This shows a simple example of building and running a C++ project on PowerPC64, a big-endian system.

## Installing

xcross may be installed via PyPi via:

```bash
pip install xcross --user
```

Or xcross may be installed via git:

```bash
git clone https://github.com/Alexhuszagh/xcross
cd xcross
python setup.py install --user
```

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
export CROSS_TARGET=alpha-unknown-linux-gnu

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

For more fine-tuned control, you can also run an interactive session within a container:

```bash
# Pull the Docker image, and run it interactively, entering the container.
xcross bash --target alpha-unknown-linux-gnu

# Clone the repository, build and run the code in the container using CMake.
git clone https://github.com/Alexhuszagh/cpp-helloworld.git
cd cpp-helloworld
mkdir build && cd build

# Build a default executable: no toolchain file required.
cmake ..
make
# Just works, as long as `add_custom_target` uses
# `${CMAKE_CROSSCOMPILING_EMULATOR} $<TARGET_FILE:..>`
# This uses Qemu as a wrapper, so running the executable
# only works on some architectures.
make run
# Can also run executables manually.
run hello

# Build a statically-linked executable.
rm -rf ./*
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/static.cmake
make
make run
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

addons:
  apt:
    update: true
    packages:
      - python3
      - python3-pip

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
      pip install xcross
      docker pull ahuszagh/cross:"$TARGET"
    fi

script:
  - |
    mkdir build && cd build
    build=
    if [ "$TARGET" != "" ] ; then
      build=xcross --target="$TARGET"
    fi
    $build cmake ..
    $build make -j 5
    $build run tests/test
```

# Using xcross

Most of the magic happens via xcross, which allows you to transparently execute commands in a Docker container. Although xcross provides simple, easy-to-use defaults, it has more configuration options for extensible cross-platform builds. Most of these command-line arguments may be provided as environment variables.

> **WARNING** By default, the root directory is shared with the Docker container, for maximum compatibility. In order to mitigate any security vulnerabilities, we run any build commands as a non-root user, and escape input in an attempt to avoid any script injections. If you are worried about a malicious build system, you may further restrict this using the `--dir` option.

### Arguments

**Fallthrough**

All arguments that are not xcross-specific are passed into the container. 

- Any trivial arguments can be passed through without issue.

```bash
# Just works
xcross make -j 5
```

- To avoid shell expansion, pass entire complex commands as a single, quoted string.

Please note that due to shell expansion, some things may evaluate on the host, and therefore may not work as expected. For example:

```bash
# This does not work in POSIX shells, since it evaluates `$CXX` in the local shell.
xcross -E CXX=cpp $CXX main.c -o main
```

In order to mitigate this, we only allow characters that could be expanded by the local shell to be passed as a single string to the container:

```bash
# Although this is escaped, we can't tell if we want a literal `$CXX`
# or want to expand it. xcross rejects this.
xcross -E CXX=cpp '$CXX' main.c -o main

# Instead, pass it as a single string. Works now.
xcross -E CXX=cpp '$CXX main.c -o main'
```

- Any environment variables and paths should be passed in POSIX style.

Although non-trivial paths that exist on Windows will be translated to POSIX style, ideally you should not rely on this.

```bash
# Doesn't work, since we use a Windows-style path to an output file.
xcross c++ main.c -o test\basic

# This does work, since it uses a POSIX-style path for the output.
xcross c++ main.c -o test/basic

# This won't work, since we use a Windows-style environment variable.
# We don't know what this is used for, so we can't convert this.
xcross -E VAR1=cpp ^%VAR1^% main.c -o main

# Works in Windows CMD, since $X doesn't expand.
xcross -E VAR1=cpp $VAR1 main.c -o main
```

**xcross Arguments**

- `--target`, `CROSS_TARGET`: The target architecture to compile to.

```bash
# These two are identical, and build for Alpha on Linux/glibc
xcross --target=alpha-unknown-linux-gnu ...
CROSS_TARGET=alpha-unknown-linux-gnu xcross ...
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
# Build for the PowerPC e500mc CPU.
export CROSS_TARGET=ppc-unknown-linux-gnu
xcross --cpu=e500mc c++ helloworld.cc -o hello
xcross --cpu=e500mc run hello
CROSS_CPU=e500mc xcross run hello
```

In order to determine valid CPU model types for the cross-compiler, you may use either of the following commands:

```bash
# Here, we probe GCC for valid CPU names for the cross-compiler.
export CROSS_TARGET=ppc-unknown-linux-gnu
xcross cc-cpu-list
# 401 403 405 405fp ... e500mc ... rs64 titan

# Here, we probe Qemu for the valid CPU names for the emulation.
xcross run-cpu-list
# 401 401a1 401b2 401c2 ... e500mc ... x2vp50 x2vp7
```

These are convenience functions around `gcc -mcpu=unknown` and `qemu-ppc -cpu help`, listing only the sorted CPU types. Note that the CPU types might not be identical for both, so it's up to the caller to properly match the CPU types.

 `--server`, `CROSS_SERVER`: The server to fetch container images from.

This defaults to `docker.io` if not provided, however, it may be explicit set to an empty string. If the server is not empty, the server is prepended to the image name.

```bash
# These are all identical.
xcross --server=docker.io ...
CROSS_SERVER=docker.io xcross ...
```

- `--username`, `CROSS_USERNAME`: The Docker Hub username for the Docker image.

This defaults to `ahuszagh` if not provided, however, it may be explicit set to an empty string. If the username is not empty, the image has the format `$username/$repository:$target`, otherwise, it has the format `$repository:$target`.

```bash
# These are all identical.
xcross --username=ahuszagh ...
CROSS_USERNAME=ahuszagh xcross ...
```

- `--repository`, `CROSS_REPOSITORY`: The name of the repository for the image.

This defaults to `cross` if not provided or is empty.

```bash
# These are all identical.
xcross --repository=cross ...
CROSS_REPOSITORY=cross xcross ...
```

- `--engine`, `CROSS_ENGINE`: The command for the container engine executable.

If not provided or empty, this searches for `docker` then `podman`.

```bash
# These are all identical.
xcross --engine=docker ...
CROSS_ENGINE=docker xcross ...
```

- `--non-interactive`, `CROSS_NONINTERACTIVE`: Disable interactive shells.

This defaults to using interactive shells if not `--non-interactive` is not provided and if `CROSS_NONINTERACTIVE` does not exist, or is set to an empty string.

```bash
# These are all identical.
xcross --non-interactive ...
CROSS_NONINTERACTIVE=1 xcross ...
```

- `--update`, `CROSS_UPDATE`: Update the container image before running.

This defaults to using the existing container version if not `--update` is not provided and if `CROSS_UPDATE` does not exist, or is set to an empty string.

```bash
# These are all identical.
xcross --update ...
CROSS_UPDATE=1 xcross ...
```

# Sharing Binaries To Host

In order to build projects and share data back to the host machine, you can use Docker's `--volume` to bind a volume from the host to client. This allows us to share a build directory between the client and host, allowing us to build binaries with inside the container and test/deploy on the host.

```bash
# On a Linux distro with SELinux, you may need to turn it
# to permissive, to enable file sharing:
#   `setenforce 0`

# Run docker image, and share current directory.
git clone https://github.com/Alexhuszagh/cpp-helloworld.git
cd cpp-helloworld
xcross --target alpha-unknown-linux-gnu

# Enter the repository, and make a platform-specific build.
cd hello
mkdir build-alpha && cd build-alpha
cmake .. -DCMAKE_TOOLCHAIN_FILE=/toolchains/static.cmake \
    -DCMAKE_BUILD_TYPE=Release
make

# Exit, and check we have our proper image.
exit
file build-alpha/hello
# build-alpha/hello: ELF 64-bit LSB executable, 
# Alpha (unofficial), version 1 (GNU/Linux), statically linked, 
# BuildID[sha1]=252707718fb090ed987a9eb9ab3a8c3f6ae93482, for 
# GNU/Linux 3.2.0, not stripped

# Please note the generated images will be owned by `root`.
ls -lh build-alpha/hello
# -rwxr-xr-x. 1 root root 2.4M May 30 20:50 build-alpha/hello
```

# Building/Running Dockerfiles

To build all Docker images, run `docker/build.sh`. To build and run a single docker image, use

```bash
image=ppcle-unknown-linux-gnu
python3 setup.py configure
docker build -t "ahuszagh/cross:$image" . --file "docker/images/Dockerfile.$image"
# Runs the image without the xcross abstraction.
docker run -it "ahuszagh/cross:$image" /bin/bash
# Runs the image using xcross, for a simpler interface.
xcross bash --target "$image"
```

# Images

For a list of pre-built images, see [DockerHub](https://hub.docker.com/r/ahuszagh/cross). To remove local, installed images from the pre-built, cross toolchains, run:

```bash
# On a POSIX shell.
images=$(docker images | grep 'ahuszagh/cross' | tr -s ' ' | cut -d ' ' -f 3)
docker rmi $images
```

**Image Types**

There are two types of images:
- Images with an OS layer, such as `ppcle-unknown-linux-gnu`.
- Bare metal images, such as `ppcle-unknown-elf`.

The bare metal images use the newlib C-runtime, and are useful for compiling for resource-constrained embedded systems, and do not link to a memory allocator. Please note that not all bare-metal images provide complete startup routines (crt0), and therefore might need to be linked against standalone flags (`-nostartfiles`, `-nostdlib`, `-nodefaultlibs`, or `-ffreestanding`) with a custom `_start` or equivalent routine or a custom `crt0` must be provided.

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
- `i386-w64-mingw32`, or `(i386, unknown, w64, mingw32)`
- `mips-unknown-o32`, `(mips, unknown, -, o32)`
- `mips-unknown-linux-gnu`, `(mips, unknown, linux, gnu)`

If an `$arch-unknown-linux-gnu` is available, then `$arch` is an alias for `$arch-unknown-linux-gnu`.

**OS/Architecture Support**

In general, the focus of these images is to provide support for a wide variety of architectures, not operating systems. We will gladly accept Dockerfiles/scripts to support more operating systems, like FreeBSD.

We do not support Darwin/iOS for licensing reasons, since reproduction of the macOS SDK is expressly forbidden. If you would like to build a Darwin cross-compiler, see [osxcross](https://github.com/tpoechtrager/osxcross).

We also do not support certain cross-compilers for popular architectures, like Hexagon, due to proprietary linkers (which would be needed for LLVM support).

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

- `/env/base`, base environment variables for cross-compiling.
- `/env/shared`, for building dynamically-linked binaries.
- `/env/static`, for building statically-linked binaries.

# Developing New Toolchains

To add your own toolchain, the general workflow is as follows:

1. List toolchain samples.
2. Configure your toolchain.
3. Move the config file to `ct-ng`.
4. Patch the config file.
5. Add the image to `config/images.json`.

After the toolchain is created, all the CMake toolchain files, symlinks, and Dockerfiles may be created with:

**config/images.json**

```jsonc
[
    // ...
    {
        // Image type (mandatory). Valid values are:
        //  1. android
        //  2. crosstool
        //  3. debian
        //  4. riscv
        //  5. other
        //
        // The following values are for crosstool images,
        // which are by far the most prevalent.
        "type": "crosstool",
        // The name of the target, resembling an LLVM triple (mandatory).
        "target": "alphaev4-unknown-linux-gnu",
        // Actual LLVM triple name, which will be the compiler prefix.
        // For example, gcc will be `alphaev4-unknown-linux-gnu-gcc`.
        // Optional, and defaults to `target`.
        "triple": "alphaev4-unknown-linux-gnu",
        // The crosstool-NG target to use. This is useful
        // when the same configuration for a multilib compiler
        // can be reused. Optional, defaults to `target`.
        "config": "alphaev4-unknown-linux-gnu",
        // Enable qemu userspace emulation (optional). Default false.
        "qemu": true,
        // Optional flags to provide to the C compiler.
        // This is useful when targeting a specific ABI,
        // or for example, to skip the default start code
        // to provide your own crt0.
        "flags": "-nostartfiles",
        // Name of the processor for Qemu user-space emulation
        // and for setting the toolchain alias.
        "processor": "alpha"
    },
    // ...
]
```

For a bare-metal example, see `ct-ng/ppcle-unknown-elf.config`. For a Linux example, see `ct-ng/ppcle-unknown-linux-gnu.config`. Be sure to add your new toolchain to `config/images.json`, and run the test suite with the new toolchain image.

# Platform Support

Currently, we only create images that are supported by:

- crosstool-NG with official sources
- Debian packages
- Android NDK's
- RISCV GNU utils.

We therefore support:

- ARM32 + Thumb (Linux, Android, Bare-Metal)
- ARM32-BE + Thumb (Linux, Android, Bare-Metal)
- ARM64 (Linux, Android, Bare-Metal)
- ARM64-BE (Linux, Android, Bare-Metal)
- alpha (Linux)
- ARC (Linux, Bare-Metal)
- AVR (Bare-Metal)
- HPPA (Linux)
- i386-i686 (Bare-Metal)
- i686 (Linux, MinGW, Android)
- m68k (Linux)
- MicroBlaze (Linux)
- MicroBlaze-LE (Linux)
- MIPS (Linux, Bare-Metal)
- MIPS-LE (Linux, Bare-Metal)
- MIPS64 (Linux, Bare-Metal)
- MIPS64-LE (Linux, Bare-Metal)
- Moxie (Bare-Metal: Moxiebox and ELF)
- Moxie-BE (Bare-Metal: ELF-only)
- NIOS2 (Linux, Bare-Metal)
- PowerPC (Linux, Bare-Metal)
- PowerPC-LE (Linux, Bare-Metal)
- PowerPC64 (Linux, Bare-Metal)
- PowerPC64-LE (Linux, Bare-Metal)
- RISCV32 (Linux, Bare-Metal)
- RISCV64 (Linux, Bare-Metal)
- s390 (Linux)  
- s390x (Linux) 
- SH1-4 (Linux, Bare-Metal)
- Sparc (Linux)
- Sparc64 (Linux)
- x86_64 (Linux, MinGW, Android, Bare-Metal)
- xtensa (Linux)

Platform-specific details:

- Xtensa does not support newlib, glibc, or musl.

# License

This is free and unencumbered software released into the public domain. This project, however, does derive off of projects that are not necessarily public domain software, such as [crosstool-NG](https://github.com/crosstool-ng/crosstool-ng), the [Android NDK](https://android.googlesource.com/platform/prebuilts/ndk/+/master/NOTICE), as well as build off of GCC, the Linux kernel headers, and the relevant C-runtime (glibc, musl, uClibc-ng). Therefore, distributing any images will be subject to the GPLv3 or later (for GCC), and GPLv2 for the Linux headers.

These licenses are only relevant if you distribute a toolchain: for merely compiling and linking code as part of a standard toolchain, the usual linking exceptions apply.

# Contributing

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in xcross by you, will be unlicensed (free and unencumbered software released into the public domain).
