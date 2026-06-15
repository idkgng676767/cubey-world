cmake_minimum_required(VERSION 3.16)
project(forza_cubey VERSION 1.0.0 LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 11)

# Find packages
find_package(OpenGL REQUIRED)
find_package(glfw3 3.3 REQUIRED)
find_package(glm REQUIRED)

# glad
add_library(glad STATIC third_party/glad/src/glad.c)
target_include_directories(glad PUBLIC include)

# Main executable
file(GLOB_RECURSE SOURCES "src/*.cpp")
add_executable(forza_cubey ${SOURCES})

target_include_directories(forza_cubey PRIVATE 
    include
    src
    ${GLFW_INCLUDE_DIRS}
    ${GLM_INCLUDE_DIRS}
)

target_link_libraries(forza_cubey 
    glad
    glfw
    OpenGL::GL
    glm::glm
)

# Platform specific
if(UNIX AND NOT APPLE)
    target_link_libraries(forza_cubey pthread dl)
elseif(APPLE)
    target_link_libraries(forza_cubey "-framework Cocoa" "-framework IOKit" "-framework CoreFoundation")
endif()

# Compiler flags
target_compile_options(forza_cubey PRIVATE 
    -O3 
    -march=native 
    -ffast-math
    -Wall
    -Wextra
)

# Install
install(TARGETS forza_cubey DESTINATION bin)
install(DIRECTORY shaders assets DESTINATION share/forza_cubey)
