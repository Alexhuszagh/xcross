#!/bin/bash
#
# Pre-built android NDK.

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
before_installed=($(apt -qq list --installed 2>/dev/null | cut -d '/' -f 1))
apt-get install --assume-yes --no-install-recommends \
    wget \
    unzip
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

# Extract pre-built Android SDK.
version=r22b
wget https://dl.google.com/android/repository/android-ndk-"$version"-linux-x86_64.zip
unzip android-ndk-"$version"-linux-x86_64.zip
rm android-ndk-"$version"-linux-x86_64.zip
mkdir -p /usr/local/toolchains
cp -r android-ndk-"$version"/toolchains/llvm /usr/local/toolchains

# Need to remove other installed targets.
prefix=/usr/local/toolchains/llvm/prebuilt/linux-x86_64
all_targets=(
    "aarch64-linux-android"
    "armv7a-linux-androideabi"
    "i686-linux-android"
    "x86_64-linux-android"
)
rm -rf "$prefix"/test
for target in "${all_targets[@]}"; do
    if [ "$target" != "$ARCH" ]; then
        base=$(echo "$target" | cut -d '-' -f 1)
        if [ "$base" = "armv7a" ]; then
            base="arm"
        fi
        rm -rf "$prefix"/"$target"
        rm -f "$prefix"/bin/"$target"*
        rm -f "$prefix"/share/man/man1/"$target"*
        rm -rf "$prefix"/lib/gcc/"$target"
        rm -rf "$prefix"/sysroot/usr/include/"$target"
        rm -rf "$prefix"/sysroot/usr/lib/"$target"
        rm -rf "$prefix"/lib64/clang/11.0.5/lib/linux/"$base"
    fi
done

# Cleanup
cd /
rm -rf /src
apt-get remove --purge --assume-yes "${diff[@]}"
apt-get autoremove --assume-yes
