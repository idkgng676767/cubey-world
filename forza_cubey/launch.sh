#!/bin/bash
# Forza Cubey World - macOS Launch Script
# Sets up the environment and runs the game

cd "$(dirname "$0")"

# Ensure we can find Homebrew libraries
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# Run the game
./build/forza_cubey "$@"
