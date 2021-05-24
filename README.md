# Toolchains

Simple toolchains for cross-compiling.

# Building/Running Dockerfiles

To build the Docker image, run `build.sh`. To run it with the installed toolchains, run `run.sh`, which will run the Dockerfile from the current directory. If you need more complex Docker configuration, simple copy the script and add in your own logic.

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
cmake -DFASTFLOAT_TEST=ON -DCMAKE_TOOLCHAIN_FILE=/toolchains/ppc64.cmake ..
make -j 2
qemu-ppc64 tests/basictest
```
