#pragma once
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <memory>
#include <string>
#include <chrono>

namespace fc {
class IGame;
class RenderEngine;
class PhysicsEngine;
class AudioEngine;

class GameEngine {
public:
    GameEngine();
    ~GameEngine();
    
    void initialize(int w, int h, const std::string& title, bool fullscreen);
    void setGame(std::unique_ptr<IGame> game);
    void run();
    void shutdown();
    
    double getDeltaTime() const { return m_deltaTime; }
    double getFPS() const { return m_fps; }
    GLFWwindow* getWindow() const { return m_window; }
    
private:
    void processInput();
    void update(double dt);
    void render();
    
    GLFWwindow* m_window = nullptr;
    std::unique_ptr<RenderEngine> m_renderer;
    std::unique_ptr<PhysicsEngine> m_physics;
    std::unique_ptr<AudioEngine> m_audio;
    std::unique_ptr<IGame> m_game;
    
    double m_deltaTime = 0.0, m_fps = 0.0;
    bool m_running = false, m_paused = false;
    std::chrono::high_resolution_clock::time_point m_lastFrame;
};

} // namespace fc
