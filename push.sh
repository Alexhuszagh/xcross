#!/bin/bash

DOCKERFILES=(
    "base"

    # Linux-gnu targets
    "alpha-unknown-linux-gnu"
    "armel-unknown-linux-gnu"
    "armelhf-unknown-linux-gnu"
    "arm64-unknown-linux-gnu"
    "hppa-unknown-linux-gnu"
    "i686-unknown-linux-gnu"
    "m68k-unknown-linux-gnu"
    "mips-unknown-linux-gnu"
    "mips64-unknown-linux-gnu"
    "mips64el-unknown-linux-gnu"
    "mips64r6-unknown-linux-gnu"
    "mips64r6el-unknown-linux-gnu"
    "mipsel-unknown-linux-gnu"
    "mipsr6-unknown-linux-gnu"
    "mipsr6el-unknown-linux-gnu"
    "ppc-unknown-linux-gnu"
    "ppcle-unknown-linux-gnu"
    "ppc64-unknown-linux-gnu"
    "ppc64le-unknown-linux-gnu"
    "riscv64-unknown-linux-gnu"
    "s390x-unknown-linux-gnu"
    "sh4-unknown-linux-gnu"
    "sparc64-unknown-linux-gnu"
    "x86_64-unknown-linux-gnu"

    # Bare-metal targets.
    "ppcle-unknown-elf"
)

for name in "${DOCKERFILES[@]}"; do
    docker push "ahuszagh/cross:$name"
    if [[ "$name" == *-unknown-linux-gnu ]]; then
        base="${name%-unknown-linux-gnu}"
        docker tag "ahuszagh/cross:$name" "ahuszagh/cross:$base"
    fi
done
