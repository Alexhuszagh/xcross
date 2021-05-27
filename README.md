# Toolchains

Simple toolchains for cross-compiling.

# Building/Running Dockerfiles

To build the Docker image, run `build.sh`. To run it with the installed toolchains, run `run.sh`, which will run the Dockerfile from the current directory. If you need more complex Docker configuration, simple copy the script and add in your own logic.

# Requirements

In order to build the toolchains, you must have:

- Docker
- Bash
- Git

Everything else runs in the container.

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

# Developing

Feel free to add new toolchains, as needed. The relevant scripts to add a new toolchain are mainly `ct-ng.sh`, which generates the relevant cross-compiler, and `ct-ng/patch.sh`, which patches the config files generated from `ct-ng menuconfig` to use more modern versions.

You should add a Dockerfile similar to `Dockerfile.ppcle-unknown-elf`, a toolchain similar to `cmake/ppcle-unknown-elf.cmake`, and an environment file similar to `env/ppcle-unknown-elf`.

Be sure to add your new toolchain to:
- `build.sh`
- `push.sh`
- `test/run.sh`

And run the test suite with the new toolchain image.

# Contributing

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in toolchains by you, will be unlicensed (free and unencumbered software released into the public domain).
