# Need to override the system name to allow CMake to configure,
# otherwise, we get errors on bare-metal systems.
SET(CMAKE_SYSTEM_NAME Generic)
SET(CMAKE_SYSTEM_PROCESSOR ppc64le)
CMAKE_POLICY(SET CMP0065 NEW)

# TODO(ahuszagh) Fix
#SET(CMAKE_FIND_ROOT_PATH "/home/crosstoolng/x-tools/powerpc64le-unknown-spe/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
