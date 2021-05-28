set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR armv7a)

# COMPILERS
# ---------
SET(prefix armv7a-linux-androideabi30)
SET(dir "/usr/local/toolchains/llvm/prebuilt/linux-x86_64")
SET(CMAKE_C_COMPILER "${dir}/bin/${prefix}-clang")
SET(CMAKE_CXX_COMPILER "${dir}/bin/${prefix}-clang++")
set(CMAKE_COMPILER_PREFIX "armv7a-linux-androideabi-")

# PATHS
# -----
set(CMAKE_FIND_ROOT_PATH "${dir}/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# OTHER
# -----
set(ARCH 32)
SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static")
