#!/bin/bash

docker build -t "ahuszagh/cross:base" . --file Dockerfile.base
docker build -t "ahuszagh/cross:alpha" . --file Dockerfile.alpha
docker build -t "ahuszagh/cross:arm" . --file Dockerfile.arm
docker build -t "ahuszagh/cross:armhf" . --file Dockerfile.armhf
docker build -t "ahuszagh/cross:arm64" . --file Dockerfile.arm64
docker build -t "ahuszagh/cross:hppa" . --file Dockerfile.hppa
docker build -t "ahuszagh/cross:i686" . --file Dockerfile.i686
docker build -t "ahuszagh/cross:m68k" . --file Dockerfile.m68k
docker build -t "ahuszagh/cross:mips" . --file Dockerfile.mips
docker build -t "ahuszagh/cross:mips64" . --file Dockerfile.mips64
docker build -t "ahuszagh/cross:mips64el" . --file Dockerfile.mips64el
docker build -t "ahuszagh/cross:mips64r6" . --file Dockerfile.mips64r6
docker build -t "ahuszagh/cross:mips64r6el" . --file Dockerfile.mips64r6el
docker build -t "ahuszagh/cross:mipsel" . --file Dockerfile.mipsel
docker build -t "ahuszagh/cross:mipsr6" . --file Dockerfile.mipsr6
docker build -t "ahuszagh/cross:mipsr6el" . --file Dockerfile.mipsr6el
docker build -t "ahuszagh/cross:ppc" . --file Dockerfile.ppc
docker build -t "ahuszagh/cross:ppc64" . --file Dockerfile.ppc64
docker build -t "ahuszagh/cross:ppc64le" . --file Dockerfile.ppc64le
docker build -t "ahuszagh/cross:riscv64" . --file Dockerfile.riscv64
docker build -t "ahuszagh/cross:s390x" . --file Dockerfile.s390x
docker build -t "ahuszagh/cross:sh4" . --file Dockerfile.sh4
docker build -t "ahuszagh/cross:sparc64" . --file Dockerfile.sparc64
docker build -t "ahuszagh/cross:x86_64" . --file Dockerfile.x86_64

# Very slow, do last.
docker build -t "ahuszagh/cross:all" . --file Dockerfile.all
