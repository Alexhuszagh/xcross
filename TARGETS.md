# Targets

A complete list of supported targets by xcross.

## Android

- aarch64-unknown-linux-android
- armv7a-unknown-linux-androideabi
- i686-unknown-linux-android
- x86_64-unknown-linux-android

## Linux

**DEC Alpha**

- alphaev[4-7]-unknown-linux-gnu
- alpha-unknown-linux-gnu

**ARC**

- arc[eb]?hs38-unknown-linux-gnu
- arc[be]?-unknown-linux-uclibc

**ARM**

- armv6-unknown-linux-gnueabi
- armv6-unknown-linux-musleabi
- armv6-unknown-linux-uclibceabi
- armeb-unknown-gnueabi
- armel-unknown-gnueabi
- armelhf-unknown-gnueabi
- arm[eb]?-unknown-musleabi
- arm[eb]?-unknown-uclibceabi
- arm64[eb]?-unknown-linux-gnu
- arm64[eb]?-unknown-linux-musl
- arm64[eb]?-unknown-linux-uclibc
- thumbeb-unknown-linux-gnueabi
- thumbel-unknown-linux-gnueabi
- thumbelhf-unknown-linux-gnueabi

**AVR**

- avr

**CSKY**

- csky-unknown-linux-gnu

**HPPA**

- hppa-unknown-linux-gnu

**m68k**

- m68k-unknown-linux-gnu
- m68k-unknown-linux-uclibc

**MicroBlaze**

- microblaze[el]?-unknown-linux-musl
- microblaze[el]?-unknown-linux-uclibc
- microblaze[el]?-xilinx-linux-gnu

**MIPS**

- mips[el]?-unknown-o32
- mips[el]?-unknown-linux-gnu
- mips[el]?-unknown-linux-musl
- mipsr6[el]?-unknown-linux-gnu
- mips64[el]?-unknown-linux-gnu
- mips64[el]?-unknown-linux-uclibcn32
- mips64[el]?-unknown-linux-uclibcn64
- mips64r6[el]?-unknown-linux-gnu

**NIOS2**

- nios2-unknown-linux-gnu

**OpenRISC**

- openrisc-unknown-linux-musl
- openrisc-unknown-linux-uclibc

**PowerPC**

- ppc[le]?-unknown-linux-gnu
- ppc[le]?-unknown-linux-musl
- ppc64[le]?-unknown-linux-gnu
- ppc64[le]?-unknown-linux-musl
- ppc-unknown-linux-uclibc

**RISC-V**

- riscv32-multilib-linux-gnu
- riscv32-\*-\*-multilib-linux-gnu
- riscv32-g-\*-unknown-linux-gnu
- riscv64-multilib-linux-gnu
- riscv64-\*-\*-multilib-linux-gnu
- riscv64-g-\*-unknown-linux-gnu
- riscv64-g-\*-unknown-linux-musl
- riscv64-g-\*-unknown-linux-uclibc
- riscv64-unknown-linux-gnu
- riscv64-unknown-linux-musl

Supports the extensions `g`, `imaf?d?c?`, and the ABIs `ilp32d?` and `lp64d?`.

**s390**

- s390-unknown-linux-gnu
- s390x-unknown-linux-gnu
- s390x-unknown-linux-musl

**SH**

- sh[3-4][be]?-unknown-linux-gnu
- sh\*[eb]?-unknown-linux-musl

**Sparc**

- sparc-unknown-linux-uclibc
- sparcv8-unknown-linux-uclibc
- sparcleon3-unknown-linux-uclibc
- sparc64-unknown-linux-gnu

**x86**

- i[3-5]86-unknown-linux-musl
- i686-multilib-linux-musl
- i686-unknown-linux-gnu
- x86_64-multilib-linux-musl
- x86_64-multilib-linux-muslx32
- x86_64-unknown-linux-gnu
- x86_64-unknown-linux-uclibc

**xtensa**

- xtensaeb-unknown-linux-uclibc

## Windows

- i386-w64-mingw32
- x86_64-w64-mingw32

## Bare-Metal

- arc[be]?-unknown-elf
- arm[eb]?-unknown-elf
- arm64[eb]?-unknown-elf
- thumb[eb]?-unknown-elf
- m68k-unknown-elf
- moxie[eb]?-none-elf
- moxie-none-moxiebox
- nios2-unknown-elf
- ppc[le]?-unknown-elf
- riscv32-unknown-elf
- riscv64-unknown-elf
- sh\*-unknown-elf
- sparc-unknown-elf
- i[3-6]86-unknown-elf
- x86_64-unknown-elf

## Other

- wasm

# Package Manager Support

All images for Linux, MinGW, and Emscripten come pre-installed with vcpkg and Conan.
