cmake_minimum_required(VERSION 3.3)
project(zlibexec)
add_executable(zlibexec zlib.cc)

if(EXISTS "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
    # Using conan
    include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
    conan_basic_setup()
    target_link_libraries(zlibexec ${CONAN_LIBS})
elseif(DEFINED VCPKG_VERBOSE)
    # Using vcpkg
    find_package(ZLIB REQUIRED)
    target_link_libraries(zlibexec ZLIB::ZLIB)
endif()

add_custom_target(run COMMAND ${CROSSCOMPILING_EMULATOR} $<TARGET_FILE:zlibexec>)
