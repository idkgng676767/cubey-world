#!/bin/bash
# FORZA CUBEY WORLD - Build Script
# Run this on your external laptop after generating the project

set -e

echo "========================================"
echo "  FORZA CUBEY WORLD - Build"
echo "========================================"

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

echo "OS: $OS"
echo "Architecture: $ARCH"

# Find dependencies
GLFW_CFLAGS="-I/opt/homebrew/include"
GLFW_LIBS="-L/opt/homebrew/lib -lglfw"

# Compiler flags
CXX=${CXX:-g++}
CXXFLAGS="-std=c++17 -O3 -ffast-math -Wall -Wextra"
CXXFLAGS="$CXXFLAGS $GLFW_CFLAGS -I/opt/homebrew/include -I./include -I./src"

# Linker flags
LDFLAGS="$GLFW_LIBS -framework OpenGL -framework Cocoa -framework IOKit -framework CoreFoundation"

# Source files
SOURCES="
    src/main.cpp
    src/engine/GameEngine.cpp
    src/renderer/RenderEngine.cpp
    src/renderer/Shader.cpp
    src/renderer/Camera.cpp
    src/renderer/Mesh.cpp
    src/renderer/Framebuffer.cpp
    src/physics/PhysicsEngine.cpp
    src/audio/AudioEngine.cpp
    src/game/ForzaGame.cpp
    src/game/Terrain.cpp
    src/game/Skybox.cpp
    src/game/Car.cpp
    src/game/ParticleSystem.cpp
    src/game/RoadNetwork.cpp
    src/game/BuildingGenerator.cpp
"

# glad source (you need to download this)
GLAD_SRC="third_party/glad/src/glad.c"
if [ ! -f "$GLAD_SRC" ]; then
    echo ""
    echo "WARNING: glad.c not found at $GLAD_SRC"
    echo "Download glad from https://glad.dav1d.de/"
    echo "  - Language: C/C++"
    echo "  - Specification: OpenGL"
    echo "  - API: gl Version 4.6"
    echo "  - Profile: Core"
    echo "  - Extensions: none needed"
    echo "Place glad.h in include/glad/ and glad.c in third_party/glad/src/"
    echo ""
    echo "For now, trying to find system OpenGL loader..."
    GLAD_SRC=""
    CXXFLAGS="$CXXFLAGS -DGL_GLEXT_PROTOTYPES"
fi

# Build
mkdir -p build
echo ""
echo "Compiling..."

if [ -n "$GLAD_SRC" ]; then
    $CXX $CXXFLAGS -c $GLAD_SRC -o build/glad.o
    OBJECTS="build/glad.o"
else
    OBJECTS=""
fi

for src in $SOURCES; do
    obj="build/$(basename $src .cpp).o"
    echo "  [CC] $src"
    $CXX $CXXFLAGS -c $src -o $obj
    OBJECTS="$OBJECTS $obj"
done

echo ""
echo "Linking..."
$CXX $CXXFLAGS $OBJECTS -o build/forza_cubey $LDFLAGS

echo ""
echo "========================================"
echo "  BUILD SUCCESSFUL"
echo "========================================"
echo "Run: ./build/forza_cubey"
echo ""

# macOS specific
if [ "$OS" = "Darwin" ]; then
    echo "macOS detected. If you get framework errors, try:"
    echo "  brew install glfw glm"
    echo "  ./compile.sh"
fi
