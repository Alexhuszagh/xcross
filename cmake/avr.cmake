# Need to override the system name to allow CMake to configure,
# otherwise, we get errors on bare-metal systems.
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR avr)
cmake_policy(SET CMP0065 NEW)

# COMPILERS
# ---------
SET(XTOOLS_DIR /home/crosstoolng/x-tools/avr)
SET(CMAKE_C_COMPILER "${XTOOLS_DIR}/bin/avr-gcc")
SET(CMAKE_CXX_COMPILER "${XTOOLS_DIR}/bin/avr-g++")
set(CMAKE_COMPILER_PREFIX powerpcle-unknown-elf-)

# PATHS
# -----
set(CMAKE_FIND_ROOT_PATH "${XTOOLS_DIR}/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# OTHER
# -----
set(ARCH 8)
SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static -Wl,--no-export-dynamic")
