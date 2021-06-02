#!/bin/bash
# Patch a ct-ng config file.

SRC="$1"
DST="$2"
if [ -z "$2" ]; then
    DST="$SRC"
fi

# Read buffer
buffer=`cat $SRC`
# Set the proper GCC version.
# Update to 10.2.0
if [ "$DISABLE_GCC" = "" ]; then
    buffer=$(echo "$buffer" | sed 's/^CT_GCC_V_8=y$/CT_GCC_V_10=y\n# CT_GCC_V_9 is not set\n# CT_GCC_V_8 is not set/')
    buffer=$(echo "$buffer" | sed 's/^CT_GCC_VERSION="8.3.0"$/CT_GCC_VERSION="10.2.0"/')
fi
# Set the proper language support (C and C++ only).
if [ "$DISABLE_LANG_SUPPORT" = "" ]; then
    buffer=$(echo "$buffer" | sed 's/^# CT_CC_LANG_CXX is not set$/CT_CC_LANG_CXX=y/')
    buffer=$(echo "$buffer" | sed 's/^CT_CC_LANG_FORTRAN=y$/# CT_CC_LANG_FORTRAN is not set/')
    buffer=$(echo "$buffer" | sed 's/^CT_CC_LANG_ADA=y$/# CT_CC_LANG_ADA is not set/')
    buffer=$(echo "$buffer" | sed 's/^CT_CC_LANG_OBJC=y$/# CT_CC_LANG_OBJC is not set/')
    buffer=$(echo "$buffer" | sed 's/^CT_CC_LANG_OBJCXX=y$/# CT_CC_LANG_OBJCXX is not set/')
    buffer=$(echo "$buffer" | sed 's/^CT_CC_LANG_GOLANG=y$/# CT_CC_LANG_GOLANG is not set/')
fi
# Fix the MinGW version
# Update to v8.0.0
if [ "$DISABLE_MINGW" = "" ]; then
    buffer=$(echo "$buffer" | sed 's/^CT_MINGW_W64_V_V6_0=y$/CT_MINGW_W64_V_V8_0=y\n# CT_MINGW_W64_V_V7_0 is not set\n# CT_MINGW_W64_V_V6_0 is not set/')
    buffer=$(echo "$buffer" | sed 's/^CT_MINGW_W64_VERSION="v6.0.0"$/CT_MINGW_W64_VERSION="v8.0.0"/')
fi
# Fix glibc6 version.
# Update to 2.31
if [ "$DISABLE_GLIBC" = "" ]; then
    buffer=$(echo "$buffer" | sed 's/^CT_GLIBC_V_2_29=y$/CT_GLIBC_V_2_31=y\n# CT_GLIBC_V_2_30 is not set\n# CT_GLIBC_V_2_29 is not set/')
    buffer=$(echo "$buffer" | sed 's/^CT_GLIBC_VERSION="2.29"$/CT_GLIBC_VERSION="2.31"/')
fi
# Fix musl version
# Update to 1.2.2, fixes security issues.
if [ "$DISABLE_MUSL" = "" ]; then
    buffer=$(echo "$buffer" | sed 's/^CT_MUSL_V_1_1_21=y$/CT_MUSL_V_1_2_2=y\n# CT_MUSL_V_1_1_21 is not set/')
    buffer=$(echo "$buffer" | sed 's/^CT_MUSL_VERSION="1.1.21"$/CT_MUSL_VERSION="1.2.2"/')
fi
# Fix the expat version.
# Update to 2.4.1, fixes security issues.
buffer=$(echo "$buffer" | sed 's/^CT_EXPAT_V_2_2=y$/CT_EXPAT_V_4_1=y\n# CT_EXPAT_V_2_2 is not set/')
buffer=$(echo "$buffer" | sed 's/^CT_EXPAT_VERSION="2.2.6"$/CT_EXPAT_VERSION="2.4.1"/')

# Write to file.
echo "$buffer" > "$DST"
