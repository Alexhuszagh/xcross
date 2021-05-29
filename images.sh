#!/bin/bash
# Get the list of all image names, bare metal and with OSes.

# Images with an OS layer.
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
    # TODO(ahuszagh) Check support for xtensa?
    #"xtensabe-unknown-linux-gnu"
    #"xtensale-unknown-linux-gnu"

    # MUSL
    "x86_64-multilib-linux-musl"

    # UCLIBC
    "x86_64-unknown-linux-uclibc"

    # Android
    #"android"  TODO(ahuszagh) Need meta images
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

# Images with compilers for multiple architecture.
export OS_MULTI_IMAGES=(
    "android"
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
    "sh1-unknown-elf"
    "sh2-unknown-elf"
    "sh2e-unknown-elf"
    "sh3-unknown-elf"
    "sh3e-unknown-elf"
    "sh4-unknown-elf"
    "sh4-100-unknown-elf"
    "sh4-200-unknown-elf"
    "sh4-300-unknown-elf"
    "sh4-340-unknown-elf"
    "sh4-500-unknown-elf"
    "sh4a-unknown-elf"
    #"sparc-unknown"
    #"sparc64-unknown"
    #"i386-unknown"
    #"i486-unknown"
    #"i586-unknown"
    #"i686-unknown"
    #"x86_64-unknown"

    # Newlib does not support Xtensa.

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

# Images with compilers for multiple architecture.
export METAL_MULTI_IMAGES=(
    "sh-unknown-elf"
    # Currently fails due to "multiple definition of `_errno'".
    #"shbe-unknown-elf"
)

export IMAGES=(
    "${OS_IMAGES[@]}"
    "${OS_MULTI_IMAGES[@]}"
    "${METAL_IMAGES[@]}"
    "${METAL_MULTI_IMAGES[@]}"
)
