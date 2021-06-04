#!/bin/bash
#
# Build GCC for RISC-V targets.

set -ex

# Check required environment variables.
if [ "$ARCH" = "" ]; then
    echo "Invalid arch, must provide a valid architecture prefix."
    exit 1
fi

export DEBIAN_FRONTEND="noninteractive"

# Install dependencies. We store the installed
# dependencies so we don't accidentally delete
# necessary files, and we get rid of everything
# that was only required for the build.
apt-get update
apt-get install --assume-yes --no-install-recommends libgmp10 libmpc3
before_installed=($(apt -qq list --installed 2>/dev/null | cut -d '/' -f 1))
apt-get install --assume-yes --no-install-recommends \
    autoconf \
    automake \
    autotools-dev \
    bc \
    binutils-dev \
    bison \
    build-essential \
    curl \
    flex \
    gawk \
    gperf \
    libexpat-dev \
    libglib2.0-dev \
    libgmp-dev \
    libmpc-dev \
    libmpfr-dev \
    libtool \
    ninja-build \
    patchutils \
    pkg-config \
    python3 \
    python3-dev \
    python3-pip \
    texinfo \
    zlib1g-dev
after_installed=($(apt -qq list --installed 2>/dev/null | cut -d '/' -f 1))

# Calculate the packages we need to remove later.
diff=()
for i in "${after_installed[@]}"; do
    skip=
    for j in "${before_installed[@]}"; do
        [[ $i == $j ]] && { skip=1; break; }
    done
    [[ -n $skip ]] || diff+=("$i")
done
declare -p diff

# Create a source directory for easy cleanup.
mkdir -p src && cd src

# Clone and checkout the proper versions
git clone --depth 1 --branch 2021.04.23 \
    https://github.com/riscv/riscv-gnu-toolchain
cd riscv-gnu-toolchain
git checkout -b toolchains

# Checkout the proper versions of all our submodules.
git config -f .gitmodules submodule.riscv-binutils.branch riscv-binutils-2.36.1
git config -f .gitmodules submodule.riscv-binutils.shallow true
git config -f .gitmodules submodule.riscv-gcc.branch riscv-gcc-10.2.0
git config -f .gitmodules submodule.riscv-gcc.shallow true
# Can't use shallow for the sourceware repositories.
# Therefore, no shallow for newlib or glibc.
git config -f .gitmodules submodule.riscv-gdb.branch fsf-gdb-10.1-with-sim
git config -f .gitmodules submodule.riscv-gdb.shallow true

git submodule update --init riscv-binutils
git submodule update --init riscv-gcc
git submodule update --init riscv-gdb

if [[ "$ARCH" == *-linux-gnu ]]; then
    # Add support for linux GNU.
    git submodule update --init riscv-glibc
    cd riscv-glibc && git checkout glibc-2.33 && cd ..
elif [[ "$ARCH" = *-unknown-elf ]]; then
    # Add support for newlib, bare metal target.
    git submodule update --init riscv-newlib
    cd riscv-newlib && git checkout newlib-4.1.0 && cd ..
else
    echo "Error: target $ARCH currently not supported."
    exit 1
fi

# Now need to configure the build and build the toolchain.
if [[ "$ARCH" = *-linux-gnu ]]; then
    ./configure --prefix=/opt/riscv --enable-linux  --enable-multilib
    make linux -j 5
elif [[ "$ARCH" = *-elf ]]; then
    ./configure --prefix=/opt/riscv --disable-linux --enable-multilib
    make
fi

# Need to strip binaries, since the installer doesn't do that
strip_shared() {
    strip=strip
    if [ "$2" != "" ]; then
        strip="$2"
    fi
    mime=$(file "$1" --mime-type | cut -d ' ' -f 2)
    # Don't strip archives: we need those symbols.
    if [ "$mime" = "application/x-sharedlib" ] || [ "$mime" = "application/x-executable" ]; then
        "$strip" "$1"
    fi
}

strip_dir() {
    files=($(ls "$1"))
    for f in "${files[@]}"; do
        strip_shared "$1/$f" "$2"
    done
}

home="/opt/riscv"
strip_native="$home/bin/"$ARCH"-strip"
strip_dir "$home/bin"
strip_dir "$home/lib"
strip_dir "$home/"$ARCH"/bin"
strip_dir "$home/libexec/gcc/"$ARCH"/10.2.0"
strip_dir "$home/sysroot/usr/lib64" "$strip_native"
strip_dir "$home/sysroot/usr/lib64/lp64" "$strip_native"
strip_dir "$home/sysroot/usr/lib64/lp64/gconv" "$strip_native"
strip_dir "$home/sysroot/usr/lib64/lp64d" "$strip_native"
strip_dir "$home/sysroot/usr/lib64/lp64d/gconv" "$strip_native"
strip_dir "$home/sysroot/usr/lib32" "$strip_native"
strip_dir "$home/sysroot/usr/lib32/ilp32" "$strip_native"
strip_dir "$home/sysroot/usr/lib32/ilp32/gconv" "$strip_native"
strip_dir "$home/sysroot/usr/lib32/ilp32d" "$strip_native"
strip_dir "$home/sysroot/usr/lib32/ilp32d/gconv" "$strip_native"

# Remove all dependencies, to ensure we have a small image.
cd /
rm -rf /src
apt-get remove --purge --assume-yes "${diff[@]}"
apt-get autoremove --assume-yes
