cmake_minimum_required(VERSION 3.3)
project(atoi)

add_executable(atoi atoi.cc)
add_custom_target(run COMMAND ${CROSSCOMPILING_EMULATOR} $<TARGET_FILE:atoi>)
