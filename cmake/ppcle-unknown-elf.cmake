# Need to override the system name to allow CMake to configure,
# otherwise, we get errors on bare-metal systems.
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ppcle)
cmake_policy(SET CMP0065 NEW)

# COMPILERS
# ---------
SET(XTOOLS_DIR /home/crosstoolng/x-tools/powerpcle-unknown-elf)
SET(CMAKE_C_COMPILER "${XTOOLS_DIR}/bin/powerpcle-unknown-elf-gcc")
SET(CMAKE_CXX_COMPILER "${XTOOLS_DIR}/bin/powerpcle-unknown-elf-g++")
set(CMAKE_COMPILER_PREFIX powerpcle-unknown-elf-)

# PATHS
# -----
set(CMAKE_FIND_ROOT_PATH "${XTOOLS_DIR}/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# OTHER
# -----
set(ARCH 32)
SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static -Wl,--no-export-dynamic")
