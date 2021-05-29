SET(CMAKE_SYSTEM_NAME Linux)
SET(CMAKE_SYSTEM_PROCESSOR x86_64)

# COMPILERS
# ---------
SET(prefix x86_64-linux-android30)
SET(dir "/usr/local/toolchains/llvm/prebuilt/linux-x86_64")
SET(CMAKE_C_COMPILER "${dir}/bin/${prefix}-clang")
SET(CMAKE_CXX_COMPILER "${dir}/bin/${prefix}-clang++")
SET(CMAKE_COMPILER_PREFIX "x86_64-linux-android-")

# PATHS
# -----
SET(CMAKE_FIND_ROOT_PATH "${dir}/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# OTHER
# -----
SET(ARCH 64)
