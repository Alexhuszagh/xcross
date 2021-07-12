# xcross

"Zero setup" cross-compilation for a wide variety of architectures. xcross includes compact docker [images](https://hub.docker.com/r/ahuszagh/cross) and a build utility for minimal setup C/C++ cross-compiling, inspired by [rust-embedded/cross](https://github.com/rust-embedded/cross). xcross provides toolchains for a wide variety of architectures and C libraries, and targets both bare-metal and Linux-based systems, making it ideal for:

- Testing cross-platform support in CI pipelines.
- Building and deploying cross-compiled programs.

Each Docker image comes pre-installed with:

- C and C++ cross compiler and standard library
- Autotools
- Binutils
- CMake
- Ninja

In addition, each xcross provides [images](https://hub.docker.com/r/ahuszagh/pkgcross) pre-installed with popular C/C++ package managers and addition build tools:

- Conan
- vcpkg
- Meson

Note that this project is similar to [dockcross](https://github.com/dockcross/dockcross), however, xcross supports more targets and build tools than dockcross. If you need Docker images of common architectures, dockcross should have better support.

**Table of Contents**

- [Motivation](#motivation)
- [Getting Started](#getting-started)
  - [Installing](#installing)
  - [xcross](#xcross)
  - [Build Tools](#build-tools)
  - [run](#run)
  - [Docker](#docker)
- [Travis CI Example](#travis-ci-example)
- [Sandboxing](#sandboxing)
- [Package Managers](#package-managers)
- [Using xcross](#using-xcross)
- [Other Utilities](#other-utilities)
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

Normally, cross compilers are limited by long compile times (to build the cross-compiler) and non-portable toolchain files, since the toolchain cannot be added to the path. Docker images pre-installed with cross-compiler toolchains solve this, by isolating the toolchain from the host, enabling building, testing, and deploying cross-compiled code in seconds, rather than hours. Each toolchain is installed on-path, and cross-compilation configurations are injected for each build system, enabling out-of-the-box cross-compilation for CMake, Autotools, Makefiles, and Meson. Finally, a Python script [xcross](https://pypi.org/project/xcross/) handles all Docker configurations to make cross-compiling as easy as compiling on the host machine.

It just works.

# Getting Started

This shows a simple example of building and running a C++ project on DEC Alpha, a 64-bit little-endian system.

## Installing

xcross may be installed via [PyPi](https://pypi.org/project/xcross/):

```bash
pip install xcross --user
```

Or xcross may be installed via git:

```bash
git clone https://github.com/Alexhuszagh/xcross
cd xcross
pip install . --user
```

## xcross

xcross is a Python script to provide "zero-setup" cross-compiling, similar to Rust's [cross](https://github.com/rust-embedded/cross). To use it, merely add `xcross` before any command along with a valid target. To configure, build, and make a CMake project, run:

```bash
export CROSS_TARGET=alpha-unknown-linux-gnu
xcross cmake ..
xcross make -j 5
```

## run

xcross includes a `run` command for most images, which uses Qemu to run the cross-compiled binaries.

```rust
xcross run path/to/file
```

`run` works for both statically and dynamically-linked binaries, ensuring linked libraries are in Qemu's search path.

## Docker

For more fine-tuned control, you can also run an interactive session within a container. An extended example is:

```bash
# Pull the Docker image, and run it interactively, entering the container.
xcross --target alpha-unknown-linux-gnu

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

# Can also use Makefiles normally. Here we prefer shared linking. 
# This environment only adds or removes the `-static` flag when 
# compiling: nothing else is modified.
cd ..
source /toolchains/shared
make
run helloworld

# Can also use static linking.
source /toolchains/static
make clean
make
run helloworld

# We can also invoke `c++` and `cc` commands directly.
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

# Sandboxing

By default, xcross shares your root directory with the image, running with the same permissions as the current user. However, you can limit the shared directories with the `--dir` option, allowing you to limit the build system to only the project files. This is useful for compiling untrusted code, providing an extra layer of security relative to running it on the host computer.

For these reasons, commands run via xcross are not given root access. If you need to install build dependencies, there a few options:

1. Get a non-root package manager such as [junest](https://github.com/fsquillace/junest) or [homebrew](https://docs.brew.sh/Homebrew-on-Linux).
2. Install dependencies locally via `apt download` and `apt-rdepends`, to install to a local prefix with `dpkg -force-not-root --root=$HOME`.
3. Creating a new Docker image that uses an xcross toolchain as a base image, for example `FROM ahuszagh/cross:<TARGET>`.

# Package Managers

When using xcross with the `--with-package-managers` option, xcross will run images that come pre-installed with vcpkg and Conan. 

If run in detached mode (via `--detach`), no limitations exist. Otherwise, a new Docker container is run for each command, losing any changes outside the shared volume, so the following caveats apply:

- `conan install` installs packages relative to the CWD. Changing the CWD may lead to missing dependencies.
- `vcpkg install` only works with manifests, not with global installs.

See [test/zlib](https://github.com/Alexhuszagh/xcross/tree/main/test/zlib) for an example project for the following code samples:

An example of using xcross with vcpkg is:

```bash
export CROSS_TARGET=alpha-unknown-linux-gnu
export CROSS_WITH_PACKAGE_MANAGERS=1
export CROSS_DETACH=1
xcross vcpkg install
xcross cmake ..
xcross cmake --build .
xcross --stop
```

An example of using xcross with conan is:

```bash
export CROSS_TARGET=alpha-unknown-linux-gnu
export CROSS_WITH_PACKAGE_MANAGERS=1
export CROSS_DETACH=1
xcross conan install ..
xcross cmake ..
xcross cmake --build .
xcross --stop
```

**Conan Issue:** Note that Conan with CMake must be used with conan_define_targets()` and `target_link_libraries(<TARGET> CONAN_PKG::<PKG-NAME>)`. With global defines, Conan fails to link the desired libraries. With target defines, it fails to find the include directories. Therefore, both must be used in conjunction.

# Using xcross

Most of the magic happens via xcross, which allows you to transparently execute commands in a Docker container. Although xcross provides simple, easy-to-use defaults, it has more configuration options for extensible cross-platform builds. Most of these command-line arguments may be provided as environment variables.

> **WARNING** By default, the root directory is shared with the Docker container, for maximum compatibility. In order to mitigate any security vulnerabilities, we run any build commands as a non-root user, and escape input in an attempt to avoid any script injections. If you are worried about a malicious build system, you may further restrict this using the `--dir` option.

## Arguments

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
xcross -E VAR1=cpp "^%VAR1^% main.c -o main"

# Works in Windows CMD, since $X doesn't expand.
xcross -E VAR1=cpp "$VAR1 main.c -o main"
```

**xcross Arguments**

- `--target`, `CROSS_TARGET`: The target architecture to compile to.

```bash
# These two are identical, and build for Alpha on Linux/glibc
xcross --target=alpha-unknown-linux-gnu ...
CROSS_TARGET=alpha-unknown-linux-gnu xcross ...
```

- `--dir`, `CROSS_DIR`: The directory to share to the container as a volume.

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

- `--image-version`, `CROSS_VERSION`: The version of the image to use.

If not provided, this will always use the latest version.

```bash
# These are all identical.
xcross --image-version=0.1 ...
CROSS_VERSION=cross xcross ...
```

- `--with-package-managers`, `CROSS_WITH_PACKAGE_MANAGERS`: Use images pre-installed with package managers.

By default, xcross uses minimal images, with a basic set of build tools and utilities. If `--with-package-managers` is provided, then xcross will instead use images with Conan and vcpkg pre-installed, at the cost of larger image sizes.

```bash
# These are all identical.
xcross --with-package-managers ...
CROSS_WITH_PACKAGE_MANAGERS=1 xcross ...
```

- `--engine`, `CROSS_ENGINE`: The command for the container engine executable.

If not provided or empty, this searches for `docker` then `podman`.

```bash
# These are all identical.
xcross --engine=docker ...
CROSS_ENGINE=docker xcross ...
```

- `--non-interactive`, `CROSS_NONINTERACTIVE`: Disable interactive shells.

This defaults to using interactive shells if `--non-interactive` is not provided and if `CROSS_NONINTERACTIVE` does not exist, or is set to an empty string.

```bash
# These are all identical.
xcross --non-interactive ...
CROSS_NONINTERACTIVE=1 xcross ...
```

- `--detach`, `CROSS_DETACH`: Start an image in detached mode and run command in image.

This allows multiple commands to be run without losing any non-local changes after command. After running all commands, you can stop the image via `--stop`.

```bash
# These are all identical.
xcross --detach ...
CROSS_DETACH=1 xcross ...
```

- `--stop`: Stop an image started in detached mode.

```bash
xcross --stop --target=alpha-unknown-linux-gnu
```

- `--update-image`, `CROSS_UPDATE_IMAGE`: Update the container image before running.

This defaults to using the existing container version if not `--update-image` is not provided and if `CROSS_UPDATE_IMAGE` does not exist, or is set to an empty string.

```bash
# These are all identical.
xcross --update-image ...
CROSS_UPDATE_IMAGE=1 xcross ...
```

- `--remove-image`, `CROSS_REMOVE_IMAGE`: Remove the container image from local storage after running the command.

```bash
# These are all identical.
xcross --remove-image ...
CROSS_REMOVE_IMAGE=1 xcross ...
```

- `--quiet`, `CROSS_QUIET`: Silence any warnings when running the image.

```bash
# These are all identical.
xcross --quiet ...
CROSS_QUIET=1 xcross ...
```

- `--verbose`, `CROSS_VERBOSE`: Print verbose debugging output when running the image.

```bash
# These are all identical.
xcross --verbose ...
CROSS_VERBOSE=1 xcross ...
```

# Other Utilities

Each image also contains a few custom utilities to probe image configurations:

- **cc-cpu-list**: List the valid CPU values to pass to `--cpu` for the C/C++ compiler.
- **run-cpu-list**: List the valid CPU values to pass to `--cpu` for Qemu.
- **target-specs**: Print basic specifications about the target architecture.
- **target-specs-full**: Print extensive specifications about the target architecture.

```bash
$ export CROSS_TARGET=ppc-unknown-linux-gnu
$ xcross target-specs
{
  "arch": "ppc",
  "os": "linux",
  "eh-frame-header": true,
  "linker-is-gnu": true,
  "target-endian": "big",
  "pic": null,
  "pie": null,
  "char-is-signed": false,
  "data-model": "ilp32"
}
```

# Building/Running Dockerfiles

To build all Docker images, run `python3 setup.py build_imagesn--with-package-managers=1`. Note that can it take up to a week to build all images. To build and run a single docker image, use:

```bash
image=ppcle-unknown-linux-gnu
python3 setup.py configure
python3 setup.py build_image --target "$image"
# Runs the image without the xcross abstraction.
docker run -it "ahuszagh/cross:$image" /bin/bash
# Runs the image using xcross, for a simpler interface.
xcross bash --target "$image"
```

# Images

For a list of pre-built images, see [ahuszagh/cross](https://hub.docker.com/r/ahuszagh/cross) and [ahuszagh/pkgcross](https://hub.docker.com/r/ahuszagh/pkgcross). To remove local, installed images from the pre-built, cross toolchains, run:

```bash
# On a POSIX shell.
images=$(docker images | grep -E 'ahuszagh/(pkg)?cross')
images=$(echo "$images" | tr -s ' ' | cut -d ' ' -f 1,2 | tr ' ' :)
docker rmi $images
```

**Image Types**

There are two types of images:
- Images with an OS layer, such as `ppcle-unknown-linux-gnu`.
- Bare metal images, such as `ppcle-unknown-elf`.

The bare metal images use the newlib C-runtime, and are useful for compiling for resource-constrained embedded systems. Please note that not all bare-metal images provide complete startup routines (crt0), and therefore might need to be linked against standalone flags (`-nostartfiles`, `-nostdlib`, `-nodefaultlibs`, or `-ffreestanding`) with a custom startup.

Other images use a C-runtime for POSIX-like build environment (such as Linux, FreeBSD, or MinGW for Windows), and include:

- musl (`*-musl`)
- glibc (`*-gnu`)
- uClibc-ng (`*-uclibc`)
- android (`*-android`, only available on some architectures)
- mingw (`*-w64-mingw32`, only available on x86)

If you would like to test if the code compiles (and optionally, runs) for a target architecture, you should generally use a `linux-gnu` image.

**Triples**

All images are named as `ahuszagh/cross:$triple` or `ahuszagh/pkgcross:$triple`, where `$triple` is the target triple. The target triple consists of:

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

In general, the focus of these images is to provide support for a wide variety of architectures, not operating systems. We will gladly accept Dockerfiles/scripts to support more operating systems, like FreeBSD. We do not support Darwin/iOS for licensing reasons, since reproduction of the macOS SDK is expressly forbidden. If you would like to build a Darwin cross-compiler, see [osxcross](https://github.com/tpoechtrager/osxcross). We also do not support certain cross-compilers for popular architectures, like Hexagon, due to proprietary linkers (which would be needed for LLVM support).

**Versioning**

Image names have an optional, trailing version, which will always use a compatible host OS, GCC, and C-runtime version. Images without a version will always use the latest available version.

- **No Version**: Alias for the latest version listed.
- **0.1**: GCC 10.x, glibc 2.31+, musl 1.2.2, uCLibc-NG 1.0.31, Android r22b, and Ubuntu 20.04.

Pre-1.0, minor versions signify backwards-incompatible changes to toolchains. Patch increments signify bug fixes, and build increments signify the addition of new toolchains.

# Dependencies

In order to use `xcross` or build toolchains, you must have:

- python (3.6+)
- docker or podman

Everything else runs in the container.

# Toolchain Files
  
These cross-compilation configurations are automatically injected if not provided. Manually overriding these defaults allows finer control over the build process.

**CMake Toolchain Files**

- `/toolchains/toolchain.cmake`, which contains the necessary configurations to cross-compile.
- `/toolchains/shared.cmake`, for building dynamically-linked binaries.
- `/toolchains/static.cmake`, for building statically-linked binaries.
  
To include an additional toolchain in addition to the default, pass `CROSS_CHAINLOAD_TOOLCHAIN_FILE` during configuration.

**Bash Environment Files**

- `/env/base`, base environment variables for cross-compiling.
- `/env/shared`, for building dynamically-linked binaries.
- `/env/static`, for building statically-linked binaries.
  
**Meson Cross Files**

- `/toolchains/cross.meson`, which contains the necessary configurations to cross-compile.
  
**Conan Settings**
  
- `~/.conan/settings.yml`, default base settings for Conan.
- `~/.conan/profiles/default`, default Conan profile.

# Developing New Toolchains

To add your own toolchain, the general workflow (for crosstool-NG or buildroot) is as follows:

1. List toolchain samples.
2. Configure your toolchain.
3. Move the config file to `ct-ng` or `buildroot`.
4. Patch the config file.
5. Add the image to `config/images.json`.

After the toolchain is created, this shows a sample image configuration to auto-generate the relevant Dockerfile, CMake toolchains, and toolchain symlinks:

**config/images.json**

```jsonc
[
    // ...
    {
        // COMMON CONFIGURATIONS

        // Image type (mandatory). Valid values are:
        //  1. android
        //  2. crosstool
        //  3. debian
        //  4. musl-cross
        //  5. riscv
        //  6. other
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
        // Flags to provide to the C compiler (optional).
        // This is useful when targeting a specific ABI,
        // or for example, to skip the default start code
        // to provide your own crt0.
        "flags": "-nostartfiles",
        // Optional flags to provide to the C compiler (optional).
        // These are flags that will not clobber existing settings,
        // for example, if `march=armv6` is provided as an optional
        // flag, then passing `-march=armv6z` will override that setting.
        "optional_flags": "",
        // Name of the processor for Qemu user-space emulation
        // and for setting the toolchain alias.
        "processor": "alpha"

        // OTHER CONFIGURATIONS

        // Numerous other configurations are also supported, such as:
        //  * `cpulist` - A hard-coded list of valid CPU values.
        //    This will override any values from `run-cpu-list` and `cc-cpu-list`.
        //    For example, on HPPA, `"cpulist": "1.0"`.
        //
        //  * `system` - Override the system component of a triple.
        //    For example, `"system": "gnuabi64"`.
        //
        //  * `os` - Override the OS component of a triple.
        //    For example, `"os": "linux"`.
        //
        //  * `vendor` - Override the vendor component of a triple.
        //    For example, `"vendor": "unknown"`.
        //
        //  * `arch` - Override the arch component of a triple.
        //    In almost all cases, it's preferable to use `processor`,
        //    which exists for this purpose.
        //
        //  * `extensions` - Specify hardware extensions for the architecture.
        //    Not available for all targets.
        //    For example, `"extensions": "imadc"`.
        //
        //  * `abi` - Specify ABI details for the architecture.
        //    Not available for all targets.
        //    For example, `"abi": "lp64d"`.
        //
        //  * `library_path` - Specify the `LD_LIBRARY_PATH` variable for Qemu.
        //    When the C-library differs but the host and target architecture
        //    are the same, it can be necessary to set this value. You may
        //    use the `$LIBPATH` variable, which specifies the sysroot for
        //    Qemu's library search path.
        //    For example, `"library_path": "$LIBPATH/lib64"`.
        //
        //  * `preload` - Specify the `LD_PRELOAD` variable for Qemu.
        //    For example, `"preload": "$LIBPATH/lib64/libstdc++.so.6"`.
    },
    // ...
]
```

For an example bare-metal crosstool-NG config file, see `ct-ng/ppcle-unknown-elf.config`. For a Linux example, see `ct-ng/ppcle-unknown-linux-gnu.config`. Be sure to add your new toolchain to `config/images.json`, and run the test suite with the new toolchain image.

# Platform Support

For a complete list of targets, see [here](https://github.com/Alexhuszagh/xcross/blob/main/TARGETS.md). For a complete list of images, see [ahuszagh/cross](https://hub.docker.com/r/ahuszagh/cross) and [ahuszagh/pkgcross](https://hub.docker.com/r/ahuszagh/pkgcross).

Currently, we only create images that are supported by:

- crosstool-NG with official sources
- Debian packages
- Android NDK's
- musl-cross-make.
- buildroot
- RISCV GNU utils.

We therefore support:

- ARM32 + Thumb (Linux, Android, Bare-Metal)
- ARM32-BE + Thumb (Linux, Android, Bare-Metal)
- ARM64 (Linux, Android, Bare-Metal)
- ARM64-BE (Linux, Android, Bare-Metal)
- alpha (Linux)
- ARC (Linux, Bare-Metal)
- ARC-BE (Linux, Bare-Metal)
- AVR (Bare-Metal)
- CSKY (Linux)
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
- OpenRISC (Linux)
- RISCV32 (Linux, Bare-Metal)
- RISCV64 (Linux, Bare-Metal)
- s390 (Linux)  
- s390x (Linux) 
- SH1-4 (Linux, Bare-Metal)
- Sparc (LEON3 and v8, Linux)
- Sparc64 (Linux)
- x86_64 (Linux, MinGW, Android, Bare-Metal)
- xtensa-BE (Linux)
- wasm

Platform-specific details:

- Xtensa does not support newlib, glibc, or musl.

# License

The code contained within the repository, except when another license exists for a directory, is unlicensed. This is free and unencumbered software released into the public domain.

However, this only pertains to the actual code contained in the repository: this project derives off of numerous other projects which use different licenses, and the images of the resulting toolchains contain software, such as Linux, GCC, glibc, and more that are under different licenses.

For example, projects used by xcross and their licenses include:

- [crosstool-NG](https://github.com/crosstool-ng/crosstool-ng): GNU GPLv2
- [musl-cross-make](https://github.com/richfelker/musl-cross-make): MIT
- [buildroot](https://buildroot.org): GNU GPLv2
- [Android NDK](https://android.googlesource.com/platform/prebuilts/ndk/+/master/NOTICE): BSD 3-Clause
- [newlib](https://www.sourceware.org/newlib/): MIT and BSD-like licenses
- [GCC](https://gcc.gnu.org/): GNU GPLv3
- [glibc](https://www.gnu.org/software/libc/): GNU LGPLv2.1 or later
- [musl](https://musl.libc.org/): MIT
- [musl](https://musl.libc.org/): MIT
- [uClibc-ng](https://www.uclibc-ng.org/): GNU LGPLv2.1
- [emscripten](https://emscripten.org/): MIT or University of Illinois/NCSA
- [LLVM](https://llvm.org/): Apache 2.0
- [binutils](https://www.gnu.org/software/binutils/): GNU GPLv2
- [Linux](https://www.linux.org/): GNU GPLv2
- [MinGW](https://osdn.net/projects/mingw/): BSD 3-Clause and GNU GPLv2
- [Ubuntu](https://ubuntu.com/): A variety of FOSS licenses

Likewise, the diffs used to patch the toolchains are subject to the licensed of the original software. See [diff/README.md](https://github.com/Alexhuszagh/xcross/blob/main/diff/README.md) for detailed license information.

The test suites for bare-metal toolchains also derive from other projects, including:

- [newlib-examples](https://github.com/cirosantilli/newlib-examples): GNU GPLv3
- [ppc_hw](https://github.com/ara4711/ppc_hw): BSD 3-Clause
- [x86-bare-metal-examples](https://github.com/cirosantilli/x86-bare-metal-examples): GNU GPLv3

These licenses are only relevant if you distribute a toolchain or you redistribute the software used to build these images: for merely compiling and linking code as part of a standard toolchain, the usual linking exceptions apply.

# Contributing

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in xcross by you, will be unlicensed (free and unencumbered software released into the public domain).

Please note that due to licensing issues, you may not submit code that uses Github Copilot, even though Github deceptively claims you retain ownership of generated code.
