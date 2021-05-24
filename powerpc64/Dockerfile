FROM ubuntu:20.04

# Update and add the cross-compiling utilities.
RUN apt update
RUN DEBIAN_FRONTEND="noninteractive" apt-get install --assume-yes --no-install-recommends \
    g++-powerpc64-linux-gnu \
    libc6-dev-ppc64-cross \
    cmake \
    git \
    ca-certificates \
    qemu-system-ppc \
    qemu-user \
    make

RUN mkdir -p /toolchains
