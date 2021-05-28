# Need to override the system name to allow CMake to configure,
# otherwise, we get errors on bare-metal systems.
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ppcle)
cmake_policy(SET CMP0065 NEW)

# COMPILERS
# ---------
SET(prefix powerpcle-unknown-eabi)
SET(dir "/home/crosstoolng/x-tools/${prefix}")
SET(CMAKE_C_COMPILER "${dir}/bin/${prefix}-gcc")
SET(CMAKE_CXX_COMPILER "${dir}/bin/${prefix}-g++")
set(CMAKE_COMPILER_PREFIX "${prefix}-")

# PATHS
# -----
set(CMAKE_FIND_ROOT_PATH "${dir}/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# OTHER
# -----
set(ARCH 32)
SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static -Wl,--no-export-dynamic")
