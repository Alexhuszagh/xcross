#!/bin/bash

docker push ahuszagh/cross:base
docker push ahuszagh/cross:alpha
docker push ahuszagh/cross:arm
docker push ahuszagh/cross:armhf
docker push ahuszagh/cross:arm64
docker push ahuszagh/cross:hppa
docker push ahuszagh/cross:i686
docker push ahuszagh/cross:m68k
docker push ahuszagh/cross:mips
docker push ahuszagh/cross:mips64
docker push ahuszagh/cross:mips64el
docker push ahuszagh/cross:mips64r6
docker push ahuszagh/cross:mips64r6el
docker push ahuszagh/cross:mipsel
docker push ahuszagh/cross:mipsr6
docker push ahuszagh/cross:mipsr6el
docker push ahuszagh/cross:ppc
docker push ahuszagh/cross:ppc64
docker push ahuszagh/cross:ppc64le
docker push ahuszagh/cross:riscv64
docker push ahuszagh/cross:s390x
docker push ahuszagh/cross:sh4
docker push ahuszagh/cross:sparc64
docker push ahuszagh/cross:x86_64

# Very slow, do last.
docker push ahuszagh/cross:all
