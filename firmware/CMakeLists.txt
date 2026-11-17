cmake_minimum_required(VERSION 3.16)
project(guardian_firmware CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(GUARDIAN_COVERAGE "Build with gcov-style coverage flags" OFF)

add_library(guardian src/guardian.cpp)
target_include_directories(guardian PUBLIC src)
target_compile_options(guardian PRIVATE -Wall -Wextra -Wpedantic -Wswitch-enum)

add_executable(guardian_cli src/main.cpp)
target_link_libraries(guardian_cli PRIVATE guardian)
target_compile_options(guardian_cli PRIVATE -Wall -Wextra -Wpedantic)

enable_testing()
add_executable(test_guardian tests/test_guardian.cpp)
target_link_libraries(test_guardian PRIVATE guardian)
target_compile_definitions(test_guardian PRIVATE TRACE_DIR="${CMAKE_CURRENT_SOURCE_DIR}/traces")
target_compile_options(test_guardian PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME guardian_logic COMMAND test_guardian)

if(GUARDIAN_COVERAGE)
  target_compile_options(guardian PRIVATE --coverage -O0)
  target_link_options(guardian PUBLIC --coverage)
endif()
