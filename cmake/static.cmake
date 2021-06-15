CMAKE_MINIMUM_REQUIRED(VERSION 3.3)
INCLUDE("${CMAKE_CURRENT_LIST_DIR}/toolchain.cmake")
STRING(REPLACE "-static" "" CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS}")
STRING(REPLACE "-shared" "" CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS}")
STRING(REPLACE "-fPIC" "" CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
STRING(REPLACE "-fPIC" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static")
