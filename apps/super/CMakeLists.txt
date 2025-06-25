# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)
set(DTC_OVERLAY_FILE 
    ${CMAKE_CURRENT_SOURCE_DIR}/super.overlay
)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

project(super)

# 添加子目录，假设 drivers/can 是当前项目的子目录
add_subdirectory(drivers/can)

# 添加外部库目录，指定二进制目录
add_subdirectory(../CommonLibrary/motorcontrollib ${CMAKE_BINARY_DIR}/motorcontrollib)

# 添加其他库
add_library(motorcontrollib INTERFACE)

target_include_directories(motorcontrollib INTERFACE
    ../CommonLibrary/motorcontrollib
)

add_library(ProtocolV4 INTERFACE)
target_include_directories(ProtocolV4 INTERFACE
    ../CommonLibrary/ProtocolV4/uavcan/.cFolder
    ../CommonLibrary/ProtocolV4/uavcan/libcanard/libcanard
)

add_library(canard INTERFACE)
target_sources(canard INTERFACE
    ../CommonLibrary/ProtocolV4/uavcan/libcanard/libcanard/canard.c
)

add_library(statemachine INTERFACE)
target_sources(statemachine INTERFACE
    ../CommonLibrary/statemachine/statemachine.c
)

add_library(algorithmlib INTERFACE)
target_sources(algorithmlib INTERFACE
    ../CommonLibrary/algorithmlib/pid.c
    ../CommonLibrary/algorithmlib/filter.c
    ../CommonLibrary/algorithmlib/s_trajectory_planning.c
    ../CommonLibrary/algorithmlib/s_posi_planning.c
)

# 包含目录
zephyr_include_directories(
    ../CommonLibrary/motorcontrollib/include
    ../CommonLibrary/ProtocolV4/uavcan/.cFolder
    ../CommonLibrary/ProtocolV4/uavcan/libcanard
    ../CommonLibrary
)

# 添加源文件到 app target
target_sources(app PRIVATE
    src/main.c
    src/mc_thread.c
)

# 链接库
target_link_libraries(app PRIVATE
    motorcontrollib
    ProtocolV4
    canard
    statemachine
    algorithmlib
)