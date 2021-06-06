#!/bin/bash
# Get the list of all image names, bare metal and with OSes.

# Images with an OS layer.
export OS_IMAGES=(
    # GNU
    "alpha-unknown-linux-gnu"
    "alphaev4-unknown-linux-gnu"
    "alphaev5-unknown-linux-gnu"
    "alphaev6-unknown-linux-gnu"
    "alphaev7-unknown-linux-gnu"
    # Fails in libc build pass 1:
    #   glibc: configure: error: The arc is not supported
    #"arc-unknown-linux-gnu"
    "arc-unknown-linux-uclibc"
    "arcbe-unknown-linux-uclibc"
    "armel-unknown-linux-gnueabi"
    "armeb-unknown-linux-gnueabi"
    "armelhf-unknown-linux-gnueabi"
    "arm64-unknown-linux-gnu"
    "arm64eb-unknown-linux-gnu"
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
    "nios2-unknown-linux-gnu"
    "ppc-unknown-linux-gnu"
    "ppcle-unknown-linux-gnu"
    "ppc64-unknown-linux-gnu"
    "ppc64le-unknown-linux-gnu"
    # Fails with custom build of stock GCC:
    #   rv32i-based targets are not supported on stock GCC.
    "riscv32-multilib-linux-gnu"
    "riscv64-multilib-linux-gnu"
    "riscv64-unknown-linux-gnu"
    "s390-unknown-linux-gnu"
    "s390x-unknown-linux-gnu"
    "sh3-unknown-linux-gnu"
    "sh3be-unknown-linux-gnu"
    # Currently fails due to undefined reference to `__fpscr_values`.
    #"sh3e-unknown-linux-gnu"
    "sh4-unknown-linux-gnu"
    "sh4be-unknown-linux-gnu"
    # Fails in libc build pass 1:
    #   glibc 2.23+ do not support only support SPARCv9, and
    #   there's bugs with older glibc versions.
    #"sparc-unknown-linux-gnu"
    # Note: requires GCC-8, due to invalid register clobbing with source and dest.
    "sparc-unknown-linux-uclibc"
    "sparc64-unknown-linux-gnu"
    "thumbel-unknown-linux-gnueabi"
    "thumbelhf-unknown-linux-gnueabi"
    "thumbeb-unknown-linux-gnueabi"
    "x86_64-unknown-linux-gnu"
    # Fails in libc build pass 2:
    #   little endian output does not match Xtensa configuration
    #"xtensa-unknown-linux-uclibc"
    # Note: Qemu currently fails, but seems to be a Qemu error, since
    # the instructions seem to all be valid.
    "xtensabe-unknown-linux-uclibc"

    # MUSL
    "i686-multilib-linux-musl"
    "x86_64-multilib-linux-musl"

    # UCLIBC
    # Fails with fatal error: pthread.h: No such file or directory
    #"i686-unknown-linux-uclibc"
    "x86_64-unknown-linux-uclibc"

    # Android
    "aarch64-unknown-linux-android"
    "armv7a-unknown-linux-androideabi"
    "i686-unknown-linux-android"
    "x86_64-unknown-linux-android"

    # MinGW
    "i386-w64-mingw32"
    "x86_64-w64-mingw32"
)

# Bare-metal machines.
# These don't use newlibs nanomalloc, so these do not support system allocators.
export METAL_IMAGES=(
    "avr"
    # Alpha images fail with:
    #   checking iconv.h usability... make[2]: *** [Makefile:7091: configure-ld] Error 1
    #"alphaev4-unknown-elf"
    #"alphaev5-unknown-elf"
    #"alphaev6-unknown-elf"
    #"alphaev7-unknown-elf"
    "arc-unknown-elf"
    "arcbe-unknown-elf"
    "arm-unknown-elf"       # TODO(ahuszagh) Incomplete
    "armbe-unknown-elf"     # TODO(ahuszagh) Incomplete
    "arm64-unknown-elf"     # TODO(ahuszagh) Incomplete
    "arm64be-unknown-elf"   # TODO(ahuszagh) Incomplete
    "m68k-unknown-elf"
    "nios2-unknown-elf"
    #"riscv32-unknown-elf"  # TODO(ahuszagh) Restore..
    #"riscv64-unknown-elf"  # TODO(ahuszagh) Restore..
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
    "sparc-unknown-elf"
    # Fails during building newlib due to:
    #   error: argument 'dirp' doesn't match prototype
    #"sparc64-unknown-elf"
    "i386-unknown-elf"
    "i486-unknown-elf"
    "i586-unknown-elf"
    "i686-unknown-elf"
    "x86_64-unknown-elf"

    # Binutils only supports s390/s390x on Linux.
    # Newlib does not support Xtensa.
    # Currently fails due to "multiple definition of `_errno'".
    #"shbe-unknown-elf"

    # ELF
    "ppc-unknown-elf"
    "ppcle-unknown-elf"
    # GCC does not support PPC64 and PPC64LE with ELF:
    #    Configuration powerpc64-unknown-elf not supported
    #"ppc64-unknown-elf"
    #"ppc64le-unknown-elf"

    # EABI
    "ppc-unknown-eabi"
    "ppcle-unknown-eabi"
    # Binutils does not support PPC64 and PPC64LE with EABI:
    #   BFD does not support target powerpc64-unknown-eabi.
    #"ppc64-unknown-eabi"
    #"ppc64le-unknown-eabi"

    # SPE
    # GCC does not support SPEELF:
    # Configuration powerpc-unknown-elfspe not supported
    #"ppc-unknown-spe"
    #"ppcle-unknown-spe"
    #"ppc64-unknown-spe"
    #"ppc64le-unknown-spe"

    # O32
    "mips-unknown-o32"
    "mipsel-unknown-o32"

    # N32
    # Fails during configuring GCC pass 2 due to:
    #    error: cannot compute suffix of object files: cannot compile
    #"mips64-unknown-n32"
    #"mips64el-unknown-n32"

    # N64
    "mips64-unknown-n64"
    "mips64el-unknown-n64"

    # THUMB
    # TODO(ahuszagh) These need to build off of arm
    #"thumbel-unknown-elf"
    #"thumbeb-unknown-elf"
)

export IMAGES=(
    "${OS_IMAGES[@]}"
    "${METAL_IMAGES[@]}"
)
