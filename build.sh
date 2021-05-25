#!/bin/bash

DOCKERFILES=(
    "base"
    "alpha"
    "arm"
    "armhf"
    "arm64"
    "hppa"
    "i686"
    "m68k"
    "mips"
    "mips64"
    "mips64el"
    "mips64r6"
    "mips64r6el"
    "mipsel"
    "mipsr6"
    "mipsr6el"
    "ppc"
    "ppc64"
    "ppc64le"
    "riscv64"
    "s390x"
    "sh4"
    "sparc64"
    "x86_64"
    # Very slow, do last.
    "all"
)

for name in "${DOCKERFILES[@]}"; do
    docker build -t "ahuszagh/cross:$name" . --file "Dockerfile.$name"
done
