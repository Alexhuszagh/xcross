#!/bin/bash
# Run all tests.

set -ex

scriptdir=`realpath $(dirname "$BASH_SOURCE")`
source "$scriptdir/../docker/images.sh"

has_started=yes
has_stopped=no
if [ "$START" != "" ]; then
    has_started=no
fi

# Generic tests
for image in "${OS_IMAGES[@]}"; do
    if [ "$has_started" = yes ] || [ "$START" = "$image" ]; then
        has_started=yes
        "$scriptdir/docker-run.sh" helloworld "$image"
    fi

    if [ "$STOP" = "$image" ]; then
        has_stopped=yes
        break
    fi
done

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

for image in "${METAL_IMAGES[@]}"; do
    if [ "$has_stopped" = yes ]; then
        break
    elif [ "$has_started" = yes ] || [ "$START" = "$image" ]; then
        has_started=yes
        if ! skip "$image"; then
            flags=$(startfiles "$image")
            FLAGS="$flags" "$scriptdir/docker-run.sh" atoi "$image"
        fi
    fi

    if [ "$STOP" = "$image" ]; then
        has_stopped=yes
        break
    fi
done

# Extensive custom OS tests.
if [ "$METAL_TESTS" != "" ]; then
    "$scriptdir/docker-run.sh" ppc_metal "ppc-unknown-elf"
fi

# Specific hardware examples.
"$scriptdir/docker-run.sh" helloworld ppc-unknown-linux-gnu e500mc
"$scriptdir/docker-run.sh" helloworld ppc64-unknown-linux-gnu power9
"$scriptdir/docker-run.sh" helloworld mips-unknown-linux-gnu 24Kf
