set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR ppcle)

# COMPILERS
# ---------
SET(XTOOLS_DIR /home/crosstoolng/x-tools/powerpcle-unknown-linux-gnu)
SET(CMAKE_C_COMPILER "${XTOOLS_DIR}/bin/powerpcle-unknown-linux-gnu-gcc")
SET(CMAKE_CXX_COMPILER "${XTOOLS_DIR}/bin/powerpcle-unknown-linux-gnu-g++")
set(CMAKE_COMPILER_PREFIX powerpcle-unknown-linux-gnu-)

# PATHS
# -----
set(CMAKE_FIND_ROOT_PATH "${XTOOLS_DIR}/")
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# OTHER
# -----
set(ARCH 32)
SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static")
