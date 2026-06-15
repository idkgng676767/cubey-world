# FORZA CUBEY WORLD

A high-performance C++ OpenGL racing game engine inspired by Forza Horizon.

## Features

- **Deferred Rendering** with G-Buffer (position, normal, albedo, material)
- **Physically Based Lighting** with Blinn-Phong specular
- **Bloom Post-Processing** with Gaussian blur
- **SSAO** (Screen Space Ambient Occlusion)
- **Tone Mapping** with Reinhard operator
- **Real-time Physics** with rigid body dynamics
- **Procedural Terrain** with FBM noise
- **Road Network** with highways, streets, and dirt roads
- **Procedural Cities** with building generation
- **Particle Systems** for smoke, dust, and exhaust
- **Multiple Camera Modes** (Chase, Hood, Bumper, Drone, Cinematic)
- **Speed-based FOV** and camera shake effects

## Controls

| Key | Action |
|-----|--------|
| W / UP | Throttle |
| S / DOWN | Reverse |
| A / LEFT | Steer Left |
| D / RIGHT | Steer Right |
| SPACE | Brake |
| LSHIFT | Handbrake |
| Q | Look Left |
| E | Look Right |
| C | Look Back |
| R | Reset Car |
| 1-5 | Camera Modes |
| ESC | Exit |
| Mouse | Orbit Camera (Chase/Drone mode) |

## Building

### Prerequisites

- C++17 compiler (g++, clang++, MSVC)
- OpenGL 4.6
- GLFW 3.3+
- GLM
- GLAD (OpenGL loader)

### Linux/macOS

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get install build-essential cmake libglfw3-dev libglm-dev

# Install dependencies (macOS)
brew install cmake glfw glm

# Generate project (run this Python script)
python3 build_forza.py

# Build
cd forza_cubey
bash compile.sh

# Or with CMake
mkdir build && cd build
cmake ..
make -j$(nproc)
```
