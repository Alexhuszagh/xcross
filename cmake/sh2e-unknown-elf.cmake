# Need to override the system name to allow CMake to configure,
# otherwise, we get errors on bare-metal systems.
SET(CMAKE_SYSTEM_NAME Generic)
SET(CMAKE_SYSTEM_PROCESSOR sh2e)
CMAKE_POLICY(SET CMP0065 NEW)

# COMPILERS
# ---------
SET(prefix sh-unknown-elf)
SET(dir "/home/crosstoolng/x-tools/${prefix}")
SET(CMAKE_C_COMPILER "${dir}/bin/${prefix}-gcc")
SET(CMAKE_CXX_COMPILER "${dir}/bin/${prefix}-g++")
SET(CMAKE_COMPILER_PREFIX "${prefix}-")

# PATHS
# -----
SET(CMAKE_FIND_ROOT_PATH "${dir}/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# OTHER
# -----
SET(ARCH 32)
ADD_COMPILE_OPTIONS(-m2e)
