# Toolchains

Simple toolchains for cross-compiling.

# Building/Running Dockerfiles

To build the Docker image, run `build.sh`. To run it with the installed toolchains, run `run.sh`, which will run the Dockerfile from the current directory. If you need more complex Docker configuration, simple copy the script and add in your own logic.

# Adding Toolchains

For a given GCC version, you can find supported architectures via `gcc --target-help`.

# Files

In order to use the cross-compiler toolchains, 2 files are provided:
- `/toolchains/*.cmake`, which is a toolchain file for use with CMake.
- `/toolchains/env`, which can be sourced to set `CC`, `CXX`, and other environment variables for other build systems.

# Example

This runs through the logic of building and running an example repository on PowerPC64, a big-endian system:

```bash
# On the host.
./build.sh
./run.sh
# In the image
git clone https://github.com/fastfloat/fast_float --depth 1
cd fast_float
mkdir build && cd build
cmake -DFASTFLOAT_TEST=ON -DCMAKE_TOOLCHAIN_FILE=/toolchains/ppc64-unknown-linux-gnu.cmake ..
make -j 2
qemu-ppc64 tests/basictest

# Using source.
source /toolchains/env
cd /
git clone https://github.com/Alexhuszagh/cpp-helloworld.git
cd cpp-helloworld
$CXX helloworld.cc
```

# Contributing

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in toolchains by you, will be unlicensed (free and unencumbered software released into the public domain).
