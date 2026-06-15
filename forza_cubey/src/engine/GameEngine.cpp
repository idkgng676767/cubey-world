#include "GameEngine.hpp"
#include <iostream>
#include <glad/glad.h>
#include "game/IGame.hpp"
#include "renderer/RenderEngine.hpp"
#include "physics/PhysicsEngine.hpp"
#include "audio/AudioEngine.hpp"

namespace fc {

GameEngine::GameEngine() = default;
GameEngine::~GameEngine() { shutdown(); }

void GameEngine::initialize(int w, int h, const std::string& title, bool fullscreen) {
    if (!glfwInit()) throw std::runtime_error("GLFW init failed");

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 6);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_SAMPLES, 4);
    glfwWindowHint(GLFW_REFRESH_RATE, 144);

    GLFWmonitor* monitor = fullscreen ? glfwGetPrimaryMonitor() : nullptr;
    m_window = glfwCreateWindow(w, h, title.c_str(), monitor, nullptr);
    if (!m_window) { glfwTerminate(); throw std::runtime_error("Window creation failed"); }

    glfwMakeContextCurrent(m_window);
    glfwSetInputMode(m_window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    glfwSwapInterval(0); // Uncapped for benchmarking

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
        throw std::runtime_error("GLAD init failed");

    std::cout << "[Engine] OpenGL " << glGetString(GL_VERSION) << "\n";
    std::cout << "[Engine] GPU: " << glGetString(GL_RENDERER) << "\n";
    std::cout << "[Engine] Vendor: " << glGetString(GL_VENDOR) << "\n";

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    glEnable(GL_MULTISAMPLE);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    m_renderer = std::make_unique<RenderEngine>(w, h);
    m_physics = std::make_unique<PhysicsEngine>();
    m_audio = std::make_unique<AudioEngine>();

    m_lastFrame = std::chrono::high_resolution_clock::now();
    m_running = true;
}

void GameEngine::setGame(std::unique_ptr<IGame> game) {
    m_game = std::move(game);
    m_game->initialize(this);
}

void GameEngine::run() {
    while (m_running && !glfwWindowShouldClose(m_window)) {
        auto now = std::chrono::high_resolution_clock::now();
        m_deltaTime = std::chrono::duration<double>(now - m_lastFrame).count();
        m_lastFrame = now;
        m_fps = 1.0 / m_deltaTime;

        glfwPollEvents();
        if (glfwGetKey(m_window, GLFW_KEY_ESCAPE) == GLFW_PRESS) m_running = false;

        processInput();
        if (!m_paused) {
            update(m_deltaTime);
            render();
        }
        glfwSwapBuffers(m_window);
    }
}

void GameEngine::processInput() {
    if (m_game) m_game->processInput(m_window, m_deltaTime);
}

void GameEngine::update(double dt) {
    if (m_game) m_game->update(dt);
    if (m_physics) m_physics->step(dt);
    if (m_audio) m_audio->update();
}

void GameEngine::render() {
    if (m_renderer) m_renderer->beginFrame();
    if (m_game) m_game->render(m_renderer.get());
    if (m_renderer) m_renderer->endFrame();
}

void GameEngine::shutdown() {
    m_running = false;
    if (m_game) m_game->shutdown();
    if (m_window) glfwDestroyWindow(m_window);
    glfwTerminate();
    std::cout << "[Engine] Shutdown complete.\n";
}

} // namespace fc
