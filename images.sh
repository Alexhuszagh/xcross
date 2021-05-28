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

    # UCLIBC
    "x86_64-unknown-linux-uclibc"

    # Android
    "aarch64-unknown-linux-android"
    "armv7a-unknown-linux-androideabi"
    "i686-unknown-linux-android"
    "x86_64-unknown-linux-android"

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
    # TODO(ahuszagh) Add toolchains for commented ones.
    "avr"
    #"alphaev4-unknown"
    #"alphaev45-unknown"
    #"alphaev5-unknown"
    #"alphaev56-unknown"
    #"alphaev6-unknown"
    #"alphaev67-unknown"
    #"arc-unknown"
    #"arcle-unknown"
    # TODO(ahuszagh) Need ARM
    #"m68k-unknown"
    #"nios2-unknown"
    #"s390-unknown"
    #"s390x-unknown"
    #"sh1-unknown"
    #"sh1eb-unknown"
    #"sh2-unknown"
    #"sh2eb-unknown"
    #"sh3-unknown"
    #"sh3eb-unknown"
    #"sh4-unknown"
    #"sh4eb-unknown"
    #"sparc-unknown"
    #"sparc64-unknown"
    #"i386-unknown"
    #"i486-unknown"
    #"i586-unknown"
    #"i686-unknown"
    #"x86_64-unknown"
    #"xtensale-unknown"
    #"xtensabe-unknown"

    # ELF
    #"ppc-unknown-elf"
    "ppcle-unknown-elf"
    #"ppc64-unknown-elf"
    #"ppc64le-unknown-elf"

    # EABI
    #"ppc-unknown-eabi"
    "ppcle-unknown-eabi"
    #"ppc64-unknown-eabi"
    #"ppc64le-unknown-eabi"

    # SPE
    #"ppc-unknown-spe"
    #"ppcle-unknown-spe"
    #"ppc64-unknown-spe"
    #"ppc64le-unknown-spe"

    # O32
    #"mips-unknown-o32"
    #"mipsel-unknown-o32"

    # N32
    #"mips64-unknown-n32"
    #"mips64el-unknown-n32"

    # N64
    #"mips64-unknown-n64"
    #"mips64el-unknown-n64"
)

export IMAGES=(
    "${OS_IMAGES[@]}"
    "${METAL_IMAGES[@]}"
)
