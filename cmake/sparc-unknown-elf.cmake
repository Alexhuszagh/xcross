# Need to override the system name to allow CMake to configure,
# otherwise, we get errors on bare-metal systems.
SET(CMAKE_SYSTEM_NAME Generic)
SET(CMAKE_SYSTEM_PROCESSOR sparc)
CMAKE_POLICY(SET CMP0065 NEW)

SET(CMAKE_FIND_ROOT_PATH "/home/crosstoolng/x-tools/sparc-unknown-elf/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)