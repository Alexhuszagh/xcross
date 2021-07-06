cmake_minimum_required(VERSION 3.3)
project(hello)

add_executable(hello helloworld.cc)
add_custom_target(run COMMAND ${CROSSCOMPILING_EMULATOR} $<TARGET_FILE:hello>)
