#!/bin/bash
# Simple shortcuts to call executables.

# Can't guarantee all files are compiled binaries, might be
# scripts that use positional arguments. Make it a script
# that called the argument. Only export shortcut if the
# command exists, which may either be a command in the path,
# or an absolute path.
shortcut() {
    if command -v "$1" &> /dev/null; then
        echo '#!/bin/bash' >> "$2"
        echo "args=\"$ARGS\"" >> "$2"
        for value in "${FLAGS[@]}"; do
            local flag="${value%\/*}"
            local ident="${value#*\/}"
            echo "if [ \"\$$ident\" != \"\" ]; then" >> "$2"
            echo "    args=\"\$args $flag\$$ident\"" >> "$2"
            echo "fi" >> "$2"
        done
        echo "$1 \$args \"\$@\"" >> "$2"
        chmod +x "$2"
        for file in "${@:3}"; do
            ln -s "$2" "$file"
        done
    fi
}

# Shortcut for a GCC-based compiler.
shortcut_gcc() {
    local prefix
    if [ "$DIR" = "" ]; then
        prefix="$PREFIX"
    else
        prefix="$DIR/bin/$PREFIX"
    fi

    local gcc
    local gxx
    if [ "$PREFIX" = "" ]; then
        gcc=gcc
        gxx=g++
    else
        gcc="$prefix"-gcc
        gxx="$prefix"-g++
    fi
    ARGS="$CFLAGS" FLAGS="-mcpu=/CPU" shortcut "$gcc" "/usr/bin/gcc" "/usr/bin/cc"
    ARGS="$CFLAGS" FLAGS="-mcpu=/CPU" shortcut "$gxx" "/usr/bin/g++" "/usr/bin/c++" "/usr/bin/cpp"

    if [ "$VER" != "" ]; then
        ARGS="$CFLAGS" FLAGS="-mcpu=/CPU" shortcut "$gcc"-"$VER" "/usr/bin/gcc" "/usr/bin/cc"
        ARGS="$CFLAGS" FLAGS="-mcpu=/CPU" shortcut "$gxx"-"$VER" "/usr/bin/g++" "/usr/bin/c++" "/usr/bin/cpp"
    fi
}

# Shortcut for a Clang-based compiler.
shortcut_clang() {
    local prefix
    if [ "$DIR" = "" ]; then
        prefix="$PREFIX"
    else
        prefix="$DIR/bin/$PREFIX"
    fi

    local clang
    local clangxx
    if [ "$PREFIX" = "" ]; then
        clang=clang
        clangxx=clang++
    else
        clang="$prefix"-clang
        clangxx="$prefix"-clang++
    fi
    ARGS="$CFLAGS" FLAGS="-mcpu=/CPU" shortcut "$clang" "/usr/bin/clang" "/usr/bin/cc"
    ARGS="$CFLAGS" FLAGS="-mcpu=/CPU" shortcut "$clangxx" "/usr/bin/clang++" "/usr/bin/c++" "/usr/bin/cpp"

    if [ "$VER" != "" ]; then
        ARGS="$CFLAGS" FLAGS="-mcpu=/CPU" shortcut "$clang"-"$VER" "/usr/bin/clang" "/usr/bin/cc"
        ARGS="$CFLAGS" FLAGS="-mcpu=/CPU" shortcut "$clangxx"-"$VER" "/usr/bin/clang++" "/usr/bin/c++" "/usr/bin/cpp"
    fi
}

# Shortcut for all the utilities.
shortcut_util() {
    if [ "$PREFIX" = "" ]; then
        echo "Error: must set a prefix for the utilities."
        exit 1
    fi

    local prefix
    if [ "$DIR" = "" ]; then
        prefix="$PREFIX"
    else
        prefix="$DIR/bin/$PREFIX"
    fi

    # Some of these might not exist, but it's fine.
    # Shortcut does nothing if the file doesn't exist.
    shortcut "$prefix"-addr2line "/usr/bin/addr2line"
    shortcut "$prefix"-ar "/usr/bin/ar"
    shortcut "$prefix"-as "/usr/bin/as"
    shortcut "$prefix"-c++filt "/usr/bin/c++filt"
    shortcut "$prefix"-dwp "/usr/bin/dwp"
    shortcut "$prefix"-elfedit "/usr/bin/elfedit"
    shortcut "$prefix"-embedspu "/usr/bin/embedspu"
    shortcut "$prefix"-gcov "/usr/bin/gcov"
    shortcut "$prefix"-gcov-dump "/usr/bin/gcov-dump"
    shortcut "$prefix"-gcov-tool "/usr/bin/gcov-tool"
    shortcut "$prefix"-gprof "/usr/bin/gprof"
    shortcut "$prefix"-ld "/usr/bin/ld"
    shortcut "$prefix"-ld.bfd "/usr/bin/ld.bfd"
    shortcut "$prefix"-ld.gold "/usr/bin/ld.gold"
    shortcut "$prefix"-lto-dump "/usr/bin/lto-dump"
    shortcut "$prefix"-nm "/usr/bin/nm"
    shortcut "$prefix"-objcopy "/usr/bin/objcopy"
    shortcut "$prefix"-objdump "/usr/bin/objdump"
    shortcut "$prefix"-ranlib "/usr/bin/ranlib"
    shortcut "$prefix"-readelf "/usr/bin/readelf"
    shortcut "$prefix"-size "/usr/bin/size"
    shortcut "$prefix"-strings "/usr/bin/strings"
    shortcut "$prefix"-strip "/usr/bin/strip"

    if [ "$VER" != "" ]; then
        shortcut "$prefix"-gcov-"$VER" "/usr/bin/gcov"
        shortcut "$prefix"-gcov-dump-"$VER" "/usr/bin/gcov-dump"
        shortcut "$prefix"-gcov-tool-"$VER" "/usr/bin/gcov-tool"
        shortcut "$prefix"-lto-dump-"$VER" "/usr/bin/lto-dump"
    fi
}

# Create a runner for the Qemu binary.
shortcut_run() {
    if [ "$ARCH" = "" ]; then
        echo "Error: Architecture for Qemu must be specified."
        exit 1
    fi

    local qemu="qemu-$ARCH"
    local ARGS
    if [ "$LIBPATH" != "" ]; then
        # Add support for executables linked to a shared libc/libc++.
        ARGS="-L $LIBPATH"
    fi
    ARGS="$ARGS" FLAGS="-cpu /CPU" shortcut "$qemu" "/usr/bin/run"
}
