FROM ubuntu:20.04

# Update and add the cross-compiling utilities.
RUN apt update
RUN DEBIAN_FRONTEND="noninteractive" apt-get install --assume-yes --no-install-recommends \
    g++-powerpc-linux-gnu \
    g++-powerpc64-linux-gnu \
    g++-powerpc64le-linux-gnu \
    libc6-powerpc-cross \
    libc6-dev-ppc64-cross \
    libc6-dev-ppc64el-cross \
    cmake \
    git \
    ca-certificates \
    qemu-user \
    make

RUN mkdir -p /toolchains
