#!/bin/bash

docker build -t "ahuszagh/cross:base" . --file Dockerfile
docker build -t "ahuszagh/cross:alpha" . --file Dockerfile-ALPHA
docker build -t "ahuszagh/cross:arm" . --file Dockerfile-ARM
docker build -t "ahuszagh/cross:armhf" . --file Dockerfile-ARMHF
docker build -t "ahuszagh/cross:arm64" . --file Dockerfile-ARM64
docker build -t "ahuszagh/cross:hppa" . --file Dockerfile-HPPA
docker build -t "ahuszagh/cross:i686" . --file Dockerfile-I686
docker build -t "ahuszagh/cross:m68k" . --file Dockerfile-M68K
docker build -t "ahuszagh/cross:mips" . --file Dockerfile-MIPS
docker build -t "ahuszagh/cross:mips64" . --file Dockerfile-MIPS64
docker build -t "ahuszagh/cross:mips64el" . --file Dockerfile-MIPS64EL
docker build -t "ahuszagh/cross:mips64r6" . --file Dockerfile-MIPS64R6
docker build -t "ahuszagh/cross:mips64r6el" . --file Dockerfile-MIPS64R6EL
docker build -t "ahuszagh/cross:mipsel" . --file Dockerfile-MIPSEL
docker build -t "ahuszagh/cross:mipsr6" . --file Dockerfile-MIPSR6
docker build -t "ahuszagh/cross:mipsr6el" . --file Dockerfile-MIPSR6EL
docker build -t "ahuszagh/cross:ppc" . --file Dockerfile-PPC
docker build -t "ahuszagh/cross:ppc64" . --file Dockerfile-PPC64
docker build -t "ahuszagh/cross:ppc64le" . --file Dockerfile-PPC64LE
docker build -t "ahuszagh/cross:riscv64" . --file Dockerfile-RISCV64
docker build -t "ahuszagh/cross:s390x" . --file Dockerfile-S390X
docker build -t "ahuszagh/cross:sh4" . --file Dockerfile-SH4
docker build -t "ahuszagh/cross:sparc64" . --file Dockerfile-SPARC64

# Very slow, do last.
docker build -t "ahuszagh/cross:all" . --file Dockerfile-ALL
