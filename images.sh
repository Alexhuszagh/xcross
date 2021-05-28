#!/bin/bash
# Get the list of all image names, bare metal and with OSes.

export OS_IMAGES=(
    # GNU
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
    # rv32i-based targets are not supported
    "riscv64-unknown-linux-gnu"
    "s390x-unknown-linux-gnu"
    "sh4-unknown-linux-gnu"
    "sparc64-unknown-linux-gnu"
    "x86_64-unknown-linux-gnu"

    # MUSL
    "x86_64-multilib-linux-musl"

    # x86_64-multilib-linux-musl
    # Add Musl, uclibc, and elf targets.
    # riscv32-hifive1-elf
    # riscv32-unknown-elf
    # sparc!
    # add avr.
    #   Maybe add in a few processors too.
)

# Bare-metal machines.
# These don't have allocators, so these do not support system allocators.
export METAL_IMAGES=(
    "avr"

    # ELF
    "ppcle-unknown-elf"

    # EABI
    #"ppcle-unknown-eabi"

    # SPE
)

export IMAGES=(
    "${OS_IMAGES[@]}"
    "${METAL_IMAGES[@]}"
)
