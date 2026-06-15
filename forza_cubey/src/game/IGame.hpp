#pragma once
#include <glad/glad.h>
#include <GLFW/glfw3.h>

namespace fc {

class GameEngine;
class RenderEngine;

class IGame {
public:
    virtual ~IGame() = default;
    virtual void initialize(GameEngine* engine) = 0;
    virtual void shutdown() = 0;
    virtual void processInput(GLFWwindow* window, float dt) = 0;
    virtual void update(float dt) = 0;
    virtual void render(RenderEngine* renderer) = 0;
    virtual void onWindowResize(int width, int height) = 0;
};

} // namespace fc
