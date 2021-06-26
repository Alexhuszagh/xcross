#!/bin/bash
# Run all tests.

set -x

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/../docker/images.sh"
cd "$scriptdir"
run="$scriptdir/run-test.sh"

has_started=yes
has_stopped=no
if [ "$START" != "" ]; then
    has_started=no
fi

# OS TESTS
# --------

# Do our "Hello World" tests for images with an OS layer,
git clone https://github.com/Alexhuszagh/cpp-helloworld.git buildtests
for image in "${OS_IMAGES[@]}"; do
    if [ "$has_started" = yes ] || [ "$START" = "$image" ]; then
        has_started=yes
        "$run" "$image" os
    fi

    if [ $? -ne 0 ]; then
        has_failed=yes
        has_stopped=yes
        break
    fi

    if [ "$STOP" = "$image" ]; then
        has_stopped=yes
        break
    fi
done

# Run a special test.
run_special() {
    if [ "$has_failed" != yes ]; then
        "$@"

        if [ $? -ne 0 ]; then
            has_failed=yes
        fi
    fi
}

# Test other images.
wasm() {
    NO_PERIPHERALS=1 TOOLCHAIN1=jsonly TOOLCHAIN2=wasm TOOLCHAIN1_FLAGS="-s WASM=0" \
        TOOLCHAIN2_FLAGS="-s WASM=1" "$@"
}
if [ "$has_started" = yes ] && [ "$has_stopped" = no ]; then
    run_special wasm "$run" wasm "script"
    CMAKE_FLAGS="-DJS_ONLY=1" run_special wasm "$run" wasm "script"

    # Test Ninja generators.
    CMAKE_FLAGS="-GNinja" run_special "$run" "${OS_IMAGES[0]}" "os"
    CMAKE_FLAGS="-GNinja" run_special wasm "$run" wasm "script"

    # Specific hardware examples.
    NORUN2=1 run_special "$run" ppc-unknown-linux-gnu os e500mc
    run_special "$run" ppc64-unknown-linux-gnu os power9
    run_special "$run" mips-unknown-linux-gnu os 24Kf
fi

# Cleanup our tests.
rm -rf buildtests

if [ "$has_failed" = yes ]; then
    exit 1
fi

# METAL TESTS
# -----------

startfiles() {
    case "$1" in
        # i[3-6]86 does not provide start files, a known bug with newlib.
        # moxie cannot find `__bss_start__` and `__bss_end__`.
        # sparc cannot find `__stack`.
        # there is no crt0 for x86_64
        i[3-7]86-unknown-elf | moxie*-none-elf | sparc-unknown-elf | x86_64-unknown-elf)
            echo "-nostartfiles"
            ;;
        *)
            ;;
    esac
}

skip() {
    # Check if we should skip a test.
    # PPCLE is linked to the proper library, which contains the
    # proper symbols, but still fails with an error:
    #   undefined reference to `_savegpr_29`.
    case "$1" in
        ppcle-unknown-elf)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Do our "atoi" tests for bare-metal images,
git clone https://github.com/Alexhuszagh/cpp-atoi.git buildtests
for image in "${METAL_IMAGES[@]}"; do
    if [ "$has_stopped" = yes ]; then
        break
    elif [ "$has_started" = yes ] || [ "$START" = "$image" ]; then
        has_started=yes
        if ! skip "$image"; then
            flags=$(startfiles "$image")
            FLAGS="$flags" "$run" "$image" metal
        fi
    fi

    if [ $? -ne 0 ]; then
        has_failed=yes
        has_stopped=yes
    fi

    if [ "$STOP" = "$image" ]; then
        has_stopped=yes
        break
    fi
done

# Clean up our tests.
rm -rf buildtests

if [ "$has_failed" = yes ]; then
    exit 1
fi

# Extensive custom OS tests.
if [ "$METAL_TESTS" != "" ] && [ "$has_stopped" = no ]; then
    COMMAND="ppc-metal" "$run" "ppc-unknown-elf" "metal"
fi
