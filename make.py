#!/usr/bin/env python3
"""
FORZA CUBEY WORLD — Complete C++ Game Engine Project Generator
Run: python3 build_forza.py
Then on your external laptop: cd forza_cubey && bash compile.sh
"""

import os
import sys
import shutil
from pathlib import Path

PROJECT_NAME = "forza_cubey"
BASE_DIR = Path(__file__).parent / PROJECT_NAME

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path

def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"  [GEN] {path}")

def generate_project():
    print("=" * 70)
    print("  FORZA CUBEY WORLD — C++ Game Engine Project Generator")
    print("=" * 70)
    print(f"Output: {BASE_DIR.resolve()}")
    print()

    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)

    # Directory structure
    dirs = {
        'src/engine': ensure_dir(BASE_DIR / 'src/engine'),
        'src/renderer': ensure_dir(BASE_DIR / 'src/renderer'),
        'src/physics': ensure_dir(BASE_DIR / 'src/physics'),
        'src/audio': ensure_dir(BASE_DIR / 'src/audio'),
        'src/game': ensure_dir(BASE_DIR / 'src/game'),
        'src/ui': ensure_dir(BASE_DIR / 'src/ui'),
        'shaders': ensure_dir(BASE_DIR / 'shaders'),
        'assets/textures': ensure_dir(BASE_DIR / 'assets/textures'),
        'assets/models': ensure_dir(BASE_DIR / 'assets/models'),
        'assets/audio': ensure_dir(BASE_DIR / 'assets/audio'),
        'tools': ensure_dir(BASE_DIR / 'tools'),
        'build': ensure_dir(BASE_DIR / 'build'),
        'third_party': ensure_dir(BASE_DIR / 'third_party'),
        'include': ensure_dir(BASE_DIR / 'include'),
    }

    # ═══════════════════════════════════════════════════════════════════
    # 1. MAIN ENTRY POINT
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/main.cpp', r'''// FORZA CUBEY WORLD — Main Entry
#include <iostream>
#include <csignal>
#include <memory>
#include "engine/GameEngine.hpp"
#include "game/ForzaGame.hpp"

std::unique_ptr<fc::GameEngine> g_engine;

void signal_handler(int sig) {
    std::cout << "\n[Signal " << sig << "] Shutdown...\n";
    if (g_engine) g_engine->shutdown();
    exit(0);
}

int main(int argc, char** argv) {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        std::cout << R"(
    ███████╗ ██████╗ ██████╗ ████████╗ █████╗     ██████╗██╗   ██╗██████╗ ███████╗██╗   ██╗
    ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔══██╗   ██╔════╝██║   ██║██╔══██╗██╔════╝╚██╗ ██╔╝
    █████╗  ██║   ██║██████╔╝   ██║   ███████║   ██║     ██║   ██║██████╔╝█████╗   ╚████╔╝ 
    ██╔══╝  ██║   ██║██╔══██╗   ██║   ██╔══██║   ██║     ██║   ██║██╔══██╗██╔══╝    ╚██╔╝  
    ██║     ╚██████╔╝██║  ██║   ██║   ██║  ██║██╗╚██████╗╚██████╔╝██████╔╝███████╗   ██║   
    ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝   
        )" << "\n\n";

        g_engine = std::make_unique<fc::GameEngine>();
        auto game = std::make_unique<fc::ForzaGame>();
        g_engine->setGame(std::move(game));
        g_engine->initialize(1920, 1080, "Forza Cubey World", false);
        g_engine->run();
        g_engine->shutdown();

    } catch (const std::exception& e) {
        std::cerr << "[FATAL] " << e.what() << "\n";
        return 1;
    }
    return 0;
}
''')

    # ═══════════════════════════════════════════════════════════════════
    # 2. ENGINE CORE
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/engine/GameEngine.hpp', r'''#pragma once
#include <memory>
#include <string>
#include <chrono>
#include <GLFW/glfw3.h>

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
''')

    write_file(BASE_DIR / 'src/engine/GameEngine.cpp', r'''#include "GameEngine.hpp"
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
''')

    # ═══════════════════════════════════════════════════════════════════
    # 3. RENDERER
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/renderer/RenderEngine.hpp', r'''#pragma once
#include <vector>
#include <memory>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include "Shader.hpp"
#include "Camera.hpp"
#include "Mesh.hpp"
#include "Framebuffer.hpp"

namespace fc {
struct DirectionalLight {
    glm::vec3 direction{0.3f, -0.8f, 0.5f};
    glm::vec3 color{1.0f, 0.95f, 0.8f};
    float intensity = 2.5f;
    glm::mat4 lightSpaceMatrix;
};

class RenderEngine {
public:
    RenderEngine(int w, int h);
    ~RenderEngine();
    
    void beginFrame();
    void endFrame();
    
    void setCamera(const Camera& cam);
    void setLight(const DirectionalLight& light);
    
    void renderMesh(const Mesh& mesh, const glm::mat4& model, const Shader& shader);
    void renderTerrain(const class Terrain& terrain, const Camera& cam);
    void renderSkybox(const class Skybox& skybox, const Camera& cam);
    void renderCar(const class Car& car, const Camera& cam);
    void renderParticles(const std::vector<struct Particle>& particles);
    
    void enableBloom(bool e) { m_bloom = e; }
    void enableSSAO(bool e) { m_ssao = e; }
    void enableMotionBlur(bool e) { m_motionBlur = e; }
    void setExposure(float e) { m_exposure = e; }
    
    Shader& getGeometryShader() { return m_geometryShader; }
    
    int getWidth() const { return m_width; }
    int getHeight() const { return m_height; }
    
private:
    int m_width, m_height;
    bool m_bloom = true, m_ssao = false, m_motionBlur = true;
    float m_exposure = 1.1f;
    
    std::unique_ptr<Framebuffer> m_gBuffer;
    std::unique_ptr<Framebuffer> m_shadowMap;
    std::unique_ptr<Framebuffer> m_sceneFB;
    std::unique_ptr<Framebuffer> m_pingPong[2];
    
    Shader m_geometryShader;
    Shader m_lightingShader;
    Shader m_shadowShader;
    Shader m_skyboxShader;
    Shader m_particleShader;
    Shader m_bloomShader;
    Shader m_tonemapShader;
    Shader m_ssaoShader;
    
    GLuint m_quadVAO = 0, m_quadVBO = 0;
    GLuint m_noiseTexture = 0;
    std::vector<glm::vec3> m_ssaoKernel;
    
    void initQuad();
    void renderQuad();
    void blurPass(GLuint input, int iterations);
    void bloomPass(GLuint input);
    void ssaoPass();
    void tonemapPass(GLuint input);
    void initSSAO();
};

} // namespace fc
''')

    write_file(BASE_DIR / 'src/renderer/RenderEngine.cpp', r'''#include "RenderEngine.hpp"
#include <glad/glad.h>
#include <iostream>
#include <random>
#include "game/Terrain.hpp"
#include "game/Skybox.hpp"
#include "game/Car.hpp"
#include "game/Particle.hpp"

namespace fc {

RenderEngine::RenderEngine(int w, int h) : m_width(w), m_height(h) {
    // G-Buffer: position, normal, albedo, material, depth
    m_gBuffer = std::make_unique<Framebuffer>(w, h, Framebuffer::GBuffer);
    // Shadow map
    m_shadowMap = std::make_unique<Framebuffer>(2048, 2048, Framebuffer::DepthOnly);
    // Scene HDR
    m_sceneFB = std::make_unique<Framebuffer>(w, h, Framebuffer::HDR | Framebuffer::Depth);
    // Ping-pong for bloom
    m_pingPong[0] = std::make_unique<Framebuffer>(w/2, h/2, Framebuffer::HDR);
    m_pingPong[1] = std::make_unique<Framebuffer>(w/2, h/2, Framebuffer::HDR);

    m_geometryShader.load("shaders/geometry.vert", "shaders/geometry.frag");
    m_lightingShader.load("shaders/lighting.vert", "shaders/lighting.frag");
    m_shadowShader.load("shaders/shadow.vert", "shaders/shadow.frag");
    m_skyboxShader.load("shaders/skybox.vert", "shaders/skybox.frag");
    m_particleShader.load("shaders/particle.vert", "shaders/particle.frag");
    m_bloomShader.load("shaders/bloom.vert", "shaders/bloom.frag");
    m_tonemapShader.load("shaders/tonemap.vert", "shaders/tonemap.frag");
    m_ssaoShader.load("shaders/ssao.vert", "shaders/ssao.frag");

    initQuad();
    initSSAO();

    std::cout << "[Renderer] " << w << "x" << h << " initialized\n";
}

RenderEngine::~RenderEngine() {
    if (m_quadVAO) glDeleteVertexArrays(1, &m_quadVAO);
    if (m_quadVBO) glDeleteBuffers(1, &m_quadVBO);
    if (m_noiseTexture) glDeleteTextures(1, &m_noiseTexture);
}

void RenderEngine::initQuad() {
    float quad[] = {-1,-1,0,0, 1,-1,1,0, -1,1,0,1, 1,1,1,1};
    glGenVertexArrays(1, &m_quadVAO);
    glGenBuffers(1, &m_quadVBO);
    glBindVertexArray(m_quadVAO);
    glBindBuffer(GL_ARRAY_BUFFER, m_quadVBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(quad), quad, GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4*sizeof(float), 0);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4*sizeof(float), (void*)(2*sizeof(float)));
    glBindVertexArray(0);
}

void RenderEngine::initSSAO() {
    std::uniform_real_distribution<float> rnd(0.0f, 1.0f);
    std::default_random_engine gen;
    for (int i = 0; i < 64; i++) {
        glm::vec3 sample(rnd(gen)*2-1, rnd(gen)*2-1, rnd(gen));
        sample = glm::normalize(sample);
        sample *= rnd(gen);
        float scale = (float)i / 64.0f;
        scale = 0.1f + scale * scale * 0.9f;
        m_ssaoKernel.push_back(sample * scale);
    }

    std::vector<glm::vec3> noise;
    for (int i = 0; i < 16; i++) {
        noise.push_back(glm::vec3(rnd(gen)*2-1, rnd(gen)*2-1, 0));
    }
    glGenTextures(1, &m_noiseTexture);
    glBindTexture(GL_TEXTURE_2D, m_noiseTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, 4, 4, 0, GL_RGB, GL_FLOAT, noise.data());
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
}

void RenderEngine::beginFrame() {
    // Geometry pass
    m_gBuffer->bind();
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

void RenderEngine::endFrame() {
    m_gBuffer->unbind();

    // Lighting pass -> m_sceneFB
    m_sceneFB->bind();
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    m_lightingShader.use();
    m_gBuffer->bindTextures();
    m_lightingShader.setInt("gPosition", 0);
    m_lightingShader.setInt("gNormal", 1);
    m_lightingShader.setInt("gAlbedo", 2);
    m_lightingShader.setInt("gMaterial", 3);
    m_lightingShader.setFloat("exposure", m_exposure);
    renderQuad();
    m_sceneFB->unbind();

    // Post-process from m_sceneFB
    GLuint sceneTex = m_sceneFB->getColorTexture();

    if (m_ssao) {
        ssaoPass();
    }

    if (m_bloom) {
        bloomPass(sceneTex);
    }

    tonemapPass(sceneTex);
}

void RenderEngine::renderQuad() {
    glBindVertexArray(m_quadVAO);
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    glBindVertexArray(0);
}

void RenderEngine::setCamera(const Camera& cam) {
    m_geometryShader.use();
    m_geometryShader.setMat4("viewProj", cam.getProjection() * cam.getView());
    m_geometryShader.setVec3("cameraPos", cam.getPosition());
}

void RenderEngine::setLight(const DirectionalLight& light) {
    m_lightingShader.use();
    m_lightingShader.setVec3("lightDir", light.direction);
    m_lightingShader.setVec3("lightColor", light.color);
    m_lightingShader.setFloat("lightIntensity", light.intensity);
}

void RenderEngine::renderMesh(const Mesh& mesh, const glm::mat4& model, const Shader& shader) {
    shader.setMat4("model", model);
    mesh.bind();
    glDrawElements(GL_TRIANGLES, mesh.getIndexCount(), GL_UNSIGNED_INT, 0);
    mesh.unbind();
}

void RenderEngine::blurPass(GLuint input, int iterations) {
    m_bloomShader.use();
    bool horizontal = true;
    for (int i = 0; i < iterations; i++) {
        m_pingPong[horizontal]->bind();
        m_bloomShader.setInt("horizontal", horizontal ? 1 : 0);
        glBindTexture(GL_TEXTURE_2D, i == 0 ? input : m_pingPong[!horizontal]->getColorTexture());
        renderQuad();
        horizontal = !horizontal;
    }
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void RenderEngine::bloomPass(GLuint input) {
    // Extract bright areas
    m_sceneFB->bind();
    glClear(GL_COLOR_BUFFER_BIT);
    // ... bright extraction shader ...
    renderQuad();

    // Blur
    blurPass(m_sceneFB->getColorTexture(), 10);

    // Composite
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    // ... composite shader ...
}

void RenderEngine::ssaoPass() {
    // SSAO computation
    m_ssaoShader.use();
    m_ssaoShader.setInt("gPosition", 0);
    m_ssaoShader.setInt("gNormal", 1);
    m_ssaoShader.setInt("texNoise", 2);
    // ... set kernel samples ...
    renderQuad();
}

void RenderEngine::tonemapPass(GLuint input) {
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glClear(GL_COLOR_BUFFER_BIT);
    m_tonemapShader.use();
    m_tonemapShader.setInt("scene", 0);
    m_tonemapShader.setFloat("exposure", m_exposure);
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, input);
    renderQuad();
}

void RenderEngine::renderTerrain(const Terrain& terrain, const Camera& cam) {
    terrain.render(*this, cam);
}

void RenderEngine::renderSkybox(const Skybox& skybox, const Camera& cam) {
    skybox.render(*this, cam);
}

void RenderEngine::renderCar(const Car& car, const Camera& cam) {
    car.render(*this, cam);
}

void RenderEngine::renderParticles(const std::vector<Particle>& particles) {
    m_particleShader.use();
    // ... particle rendering ...
}

} // namespace fc
''')

    # Shader class
    write_file(BASE_DIR / 'src/renderer/Shader.hpp', r'''#pragma once
#include <string>
#include <glm/glm.hpp>
#include <glad/glad.h>

namespace fc {
class Shader {
public:
    Shader() = default;
    ~Shader();
    void load(const std::string& vertPath, const std::string& fragPath);
    void use() const;
    void setBool(const std::string& n, bool v) const;
    void setInt(const std::string& n, int v) const;
    void setFloat(const std::string& n, float v) const;
    void setVec2(const std::string& n, const glm::vec2& v) const;
    void setVec3(const std::string& n, const glm::vec3& v) const;
    void setVec4(const std::string& n, const glm::vec4& v) const;
    void setMat4(const std::string& n, const glm::mat4& v) const;
    GLuint getID() const { return m_id; }
private:
    GLuint m_id = 0;
    std::string loadFile(const std::string& path);
    GLuint compileShader(const std::string& src, GLenum type);
    void linkProgram(GLuint v, GLuint f);
};
} // namespace fc
''')

    write_file(BASE_DIR / 'src/renderer/Shader.cpp', r'''#include "Shader.hpp"
#include <fstream>
#include <sstream>
#include <iostream>

namespace fc {

Shader::~Shader() { if (m_id) glDeleteProgram(m_id); }

void Shader::load(const std::string& vertPath, const std::string& fragPath) {
    auto vertSrc = loadFile(vertPath);
    auto fragSrc = loadFile(fragPath);
    GLuint vs = compileShader(vertSrc, GL_VERTEX_SHADER);
    GLuint fs = compileShader(fragSrc, GL_FRAGMENT_SHADER);
    linkProgram(vs, fs);
    glDeleteShader(vs);
    glDeleteShader(fs);
}

std::string Shader::loadFile(const std::string& path) {
    std::ifstream f(path);
    if (!f.is_open()) {
        std::cerr << "[Shader] Missing: " << path << "\n";
        return "";
    }
    std::stringstream b;
    b << f.rdbuf();
    return b.str();
}

GLuint Shader::compileShader(const std::string& src, GLenum type) {
    GLuint s = glCreateShader(type);
    const char* c = src.c_str();
    glShaderSource(s, 1, &c, nullptr);
    glCompileShader(s);
    GLint ok;
    glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[512];
        glGetShaderInfoLog(s, 512, nullptr, log);
        std::cerr << "[Shader] Compile error:\n" << log << "\n";
    }
    return s;
}

void Shader::linkProgram(GLuint v, GLuint f) {
    m_id = glCreateProgram();
    glAttachShader(m_id, v);
    glAttachShader(m_id, f);
    glLinkProgram(m_id);
    GLint ok;
    glGetProgramiv(m_id, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[512];
        glGetProgramInfoLog(m_id, 512, nullptr, log);
        std::cerr << "[Shader] Link error:\n" << log << "\n";
    }
}

void Shader::use() const { glUseProgram(m_id); }
void Shader::setBool(const std::string& n, bool v) const { glUniform1i(glGetUniformLocation(m_id, n.c_str()), v); }
void Shader::setInt(const std::string& n, int v) const { glUniform1i(glGetUniformLocation(m_id, n.c_str()), v); }
void Shader::setFloat(const std::string& n, float v) const { glUniform1f(glGetUniformLocation(m_id, n.c_str()), v); }
void Shader::setVec2(const std::string& n, const glm::vec2& v) const { glUniform2fv(glGetUniformLocation(m_id, n.c_str()), 1, &v[0]); }
void Shader::setVec3(const std::string& n, const glm::vec3& v) const { glUniform3fv(glGetUniformLocation(m_id, n.c_str()), 1, &v[0]); }
void Shader::setVec4(const std::string& n, const glm::vec4& v) const { glUniform4fv(glGetUniformLocation(m_id, n.c_str()), 1, &v[0]); }
void Shader::setMat4(const std::string& n, const glm::mat4& v) const { glUniformMatrix4fv(glGetUniformLocation(m_id, n.c_str()), 1, GL_FALSE, &v[0][0]); }

} // namespace fc
''')

    # Camera
    write_file(BASE_DIR / 'src/renderer/Camera.hpp', r'''#pragma once
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

namespace fc {
class Camera {
public:
    Camera(float fov, float aspect, float near, float far);
    void setPosition(const glm::vec3& p);
    void setTarget(const glm::vec3& t);
    void setUp(const glm::vec3& u);
    void follow(const glm::vec3& target, float dist, float height, float yaw, float pitch, float lag, float dt);
    glm::mat4 getView() const;
    glm::mat4 getProjection() const;
    glm::vec3 getPosition() const { return m_pos; }
    glm::vec3 getForward() const;
    glm::vec3 getRight() const;
    void setFOV(float fov);
    float getFOV() const { return m_fov; }
private:
    glm::vec3 m_pos{0,5,10}, m_target{0,0,0}, m_up{0,1,0};
    float m_fov, m_aspect, m_near, m_far;
    glm::vec3 m_smoothPos, m_smoothTarget;
};
} // namespace fc
''')

    write_file(BASE_DIR / 'src/renderer/Camera.cpp', r'''#include "Camera.hpp"
#include <cmath>

namespace fc {

Camera::Camera(float fov, float a, float n, float f) : m_fov(fov), m_aspect(a), m_near(n), m_far(f) {
    m_smoothPos = m_pos;
    m_smoothTarget = m_target;
}

void Camera::setPosition(const glm::vec3& p) { m_pos = p; }
void Camera::setTarget(const glm::vec3& t) { m_target = t; }
void Camera::setUp(const glm::vec3& u) { m_up = u; }

void Camera::follow(const glm::vec3& target, float dist, float height, float yaw, float pitch, float lag, float dt) {
    float t = 1.0f - std::exp(-lag * 60.0f * dt);
    m_smoothTarget += (target - m_smoothTarget) * t;

    float cy = std::cos(yaw), sy = std::sin(yaw);
    float cp = std::cos(pitch), sp = std::sin(pitch);

    glm::vec3 desired = m_smoothTarget + glm::vec3(
        sy * cp * dist,
        sp * dist + height,
        cy * cp * dist
    );

    m_smoothPos += (desired - m_smoothPos) * t;
    m_pos = m_smoothPos;
    m_target = m_smoothTarget;
}

glm::mat4 Camera::getView() const {
    return glm::lookAt(m_pos, m_target, m_up);
}

glm::mat4 Camera::getProjection() const {
    return glm::perspective(glm::radians(m_fov), m_aspect, m_near, m_far);
}

glm::vec3 Camera::getForward() const {
    return glm::normalize(m_target - m_pos);
}

glm::vec3 Camera::getRight() const {
    return glm::normalize(glm::cross(getForward(), m_up));
}

void Camera::setFOV(float fov) {
    m_fov = fov;
}

} // namespace fc
''')

    # Mesh
    write_file(BASE_DIR / 'src/renderer/Mesh.hpp', r'''#pragma once
#include <vector>
#include <glm/glm.hpp>
#include <glad/glad.h>

namespace fc {

struct Vertex {
    glm::vec3 position;
    glm::vec3 normal;
    glm::vec2 texCoord;
    glm::vec3 tangent;
    glm::vec3 bitangent;
    glm::vec4 color{1,1,1,1};
};

struct Material {
    glm::vec3 albedo{1,1,1};
    float metallic = 0.0f, roughness = 0.5f, ao = 1.0f;
    GLuint albedoMap = 0, normalMap = 0, metallicMap = 0, roughnessMap = 0, aoMap = 0;
};

class Mesh {
public:
    Mesh();
    ~Mesh();
    void load(const std::vector<Vertex>& verts, const std::vector<unsigned int>& idx);
    void generatePlane(float w, float d, int subs);
    void generateCube(float s);
    void generateSphere(float r, int segs);
    void generateCylinder(float r, float h, int segs);
    void generateTorus(float majorR, float minorR, int majorSegs, int minorSegs);
    void bind() const;
    void unbind() const;
    unsigned int getIndexCount() const { return m_indexCount; }
    void setMaterial(const Material* m) { m_material = m; }
    const Material* getMaterial() const { return m_material; }
private:
    GLuint m_vao = 0, m_vbo = 0, m_ebo = 0;
    unsigned int m_indexCount = 0;
    const Material* m_material = nullptr;
    void setupBuffers(const std::vector<Vertex>& verts, const std::vector<unsigned int>& idx);
};

} // namespace fc
''')

    write_file(BASE_DIR / 'src/renderer/Mesh.cpp', r'''#include "Mesh.hpp"
#include <cmath>

namespace fc {

Mesh::Mesh() = default;
Mesh::~Mesh() {
    if (m_vao) glDeleteVertexArrays(1, &m_vao);
    if (m_vbo) glDeleteBuffers(1, &m_vbo);
    if (m_ebo) glDeleteBuffers(1, &m_ebo);
}

void Mesh::setupBuffers(const std::vector<Vertex>& verts, const std::vector<unsigned int>& idx) {
    m_indexCount = idx.size();
    glGenVertexArrays(1, &m_vao);
    glGenBuffers(1, &m_vbo);
    glGenBuffers(1, &m_ebo);

    glBindVertexArray(m_vao);
    glBindBuffer(GL_ARRAY_BUFFER, m_vbo);
    glBufferData(GL_ARRAY_BUFFER, verts.size() * sizeof(Vertex), verts.data(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, m_ebo);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx.size() * sizeof(unsigned int), idx.data(), GL_STATIC_DRAW);

    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)0);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, normal));
    glEnableVertexAttribArray(2);
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, texCoord));
    glEnableVertexAttribArray(3);
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, tangent));
    glEnableVertexAttribArray(4);
    glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, bitangent));
    glEnableVertexAttribArray(5);
    glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, color));

    glBindVertexArray(0);
}

void Mesh::load(const std::vector<Vertex>& verts, const std::vector<unsigned int>& idx) {
    setupBuffers(verts, idx);
}

void Mesh::generatePlane(float w, float d, int subs) {
    std::vector<Vertex> verts;
    std::vector<unsigned int> idx;
    float dx = w / subs, dz = d / subs;
    float du = 1.0f / subs, dv = 1.0f / subs;

    for (int z = 0; z <= subs; z++) {
        for (int x = 0; x <= subs; x++) {
            Vertex v;
            v.position = {x * dx - w/2, 0, z * dz - d/2};
            v.normal = {0, 1, 0};
            v.texCoord = {x * du, z * dv};
            v.tangent = {1, 0, 0};
            v.bitangent = {0, 0, 1};
            verts.push_back(v);
        }
    }
    for (int z = 0; z < subs; z++) {
        for (int x = 0; x < subs; x++) {
            int i0 = z * (subs + 1) + x;
            int i1 = i0 + 1;
            int i2 = i0 + (subs + 1);
            int i3 = i2 + 1;
            idx.push_back(i0); idx.push_back(i2); idx.push_back(i1);
            idx.push_back(i1); idx.push_back(i2); idx.push_back(i3);
        }
    }
    setupBuffers(verts, idx);
}

void Mesh::generateCube(float s) {
    float h = s / 2;
    std::vector<Vertex> verts = {
        // Front
        {{-h,-h,h},{0,0,1},{0,0},{1,0,0},{0,1,0},{1,1,1,1}},
        {{ h,-h,h},{0,0,1},{1,0},{1,0,0},{0,1,0},{1,1,1,1}},
        {{ h, h,h},{0,0,1},{1,1},{1,0,0},{0,1,0},{1,1,1,1}},
        {{-h, h,h},{0,0,1},{0,1},{1,0,0},{0,1,0},{1,1,1,1}},
        // Back
        {{ h,-h,-h},{0,0,-1},{0,0},{-1,0,0},{0,1,0},{1,1,1,1}},
        {{-h,-h,-h},{0,0,-1},{1,0},{-1,0,0},{0,1,0},{1,1,1,1}},
        {{-h, h,-h},{0,0,-1},{1,1},{-1,0,0},{0,1,0},{1,1,1,1}},
        {{ h, h,-h},{0,0,-1},{0,1},{-1,0,0},{0,1,0},{1,1,1,1}},
        // Top
        {{-h,h,h},{0,1,0},{0,0},{1,0,0},{0,0,-1},{1,1,1,1}},
        {{ h,h,h},{0,1,0},{1,0},{1,0,0},{0,0,-1},{1,1,1,1}},
        {{ h,h,-h},{0,1,0},{1,1},{1,0,0},{0,0,-1},{1,1,1,1}},
        {{-h,h,-h},{0,1,0},{0,1},{1,0,0},{0,0,-1},{1,1,1,1}},
        // Bottom
        {{-h,-h,-h},{0,-1,0},{0,0},{1,0,0},{0,0,1},{1,1,1,1}},
        {{ h,-h,-h},{0,-1,0},{1,0},{1,0,0},{0,0,1},{1,1,1,1}},
        {{ h,-h,h},{0,-1,0},{1,1},{1,0,0},{0,0,1},{1,1,1,1}},
        {{-h,-h,h},{0,-1,0},{0,1},{1,0,0},{0,0,1},{1,1,1,1}},
        // Right
        {{ h,-h,h},{1,0,0},{0,0},{0,0,1},{0,1,0},{1,1,1,1}},
        {{ h,-h,-h},{1,0,0},{1,0},{0,0,1},{0,1,0},{1,1,1,1}},
        {{ h, h,-h},{1,0,0},{1,1},{0,0,1},{0,1,0},{1,1,1,1}},
        {{ h, h,h},{1,0,0},{0,1},{0,0,1},{0,1,0},{1,1,1,1}},
        // Left
        {{-h,-h,-h},{-1,0,0},{0,0},{0,0,-1},{0,1,0},{1,1,1,1}},
        {{-h,-h,h},{-1,0,0},{1,0},{0,0,-1},{0,1,0},{1,1,1,1}},
        {{-h, h,h},{-1,0,0},{1,1},{0,0,-1},{0,1,0},{1,1,1,1}},
        {{-h, h,-h},{-1,0,0},{0,1},{0,0,-1},{0,1,0},{1,1,1,1}},
    };
    std::vector<unsigned int> idx = {
        0,1,2,0,2,3, 4,5,6,4,6,7, 8,9,10,8,10,11,
        12,13,14,12,14,15, 16,17,18,16,18,19, 20,21,22,20,22,23
    };
    setupBuffers(verts, idx);
}

void Mesh::generateSphere(float r, int segs) {
    std::vector<Vertex> verts;
    std::vector<unsigned int> idx;
    for (int y = 0; y <= segs; y++) {
        float v = (float)y / segs;
        float phi = v * 3.14159f;
        for (int x = 0; x <= segs; x++) {
            float u = (float)x / segs;
            float theta = u * 2 * 3.14159f;
            float sp = std::sin(phi), cp = std::cos(phi);
            float st = std::sin(theta), ct = std::cos(theta);
            Vertex vrt;
            vrt.position = {r * sp * ct, r * cp, r * sp * st};
            vrt.normal = glm::normalize(vrt.position);
            vrt.texCoord = {u, v};
            vrt.tangent = {-st, 0, ct};
            vrt.bitangent = glm::cross(vrt.normal, vrt.tangent);
            verts.push_back(vrt);
        }
    }
    for (int y = 0; y < segs; y++) {
        for (int x = 0; x < segs; x++) {
            int i0 = y * (segs + 1) + x;
            int i1 = i0 + 1;
            int i2 = i0 + (segs + 1);
            int i3 = i2 + 1;
            if (y != 0) { idx.push_back(i0); idx.push_back(i2); idx.push_back(i1); }
            if (y != segs - 1) { idx.push_back(i1); idx.push_back(i2); idx.push_back(i3); }
        }
    }
    setupBuffers(verts, idx);
}

void Mesh::generateCylinder(float rad, float h, int segs) {
    std::vector<Vertex> verts;
    std::vector<unsigned int> idx;
    float h2 = h / 2;

    // Top center
    Vertex tc; tc.position = {0, h2, 0}; tc.normal = {0, 1, 0}; tc.texCoord = {0.5f, 0.5f};
    verts.push_back(tc);
    // Bottom center
    Vertex bc; bc.position = {0, -h2, 0}; bc.normal = {0, -1, 0}; bc.texCoord = {0.5f, 0.5f};
    verts.push_back(bc);

    for (int i = 0; i <= segs; i++) {
        float a = (float)i / segs * 2 * 3.14159f;
        float c = std::cos(a), s = std::sin(a);

        Vertex v1; v1.position = {rad * c, h2, rad * s}; v1.normal = {0, 1, 0};
        v1.texCoord = {c * 0.5f + 0.5f, s * 0.5f + 0.5f};
        verts.push_back(v1);

        Vertex v2; v2.position = {rad * c, -h2, rad * s}; v2.normal = {0, -1, 0};
        v2.texCoord = {c * 0.5f + 0.5f, s * 0.5f + 0.5f};
        verts.push_back(v2);

        Vertex v3; v3.position = {rad * c, h2, rad * s}; v3.normal = {c, 0, s};
        v3.texCoord = {(float)i / segs, 1}; v3.tangent = {-s, 0, c};
        verts.push_back(v3);

        Vertex v4; v4.position = {rad * c, -h2, rad * s}; v4.normal = {c, 0, s};
        v4.texCoord = {(float)i / segs, 0}; v4.tangent = {-s, 0, c};
        verts.push_back(v4);
    }

    int rs = 2, ss = rs + (segs + 1) * 2;
    for (int i = 0; i < segs; i++) {
        idx.push_back(0); idx.push_back(rs + i * 2); idx.push_back(rs + ((i + 1) % segs) * 2);
        idx.push_back(1); idx.push_back(rs + ((i + 1) % segs) * 2 + 1); idx.push_back(rs + i * 2 + 1);
        int i0 = ss + i * 2, i1 = ss + ((i + 1) % segs) * 2;
        int i2 = ss + i * 2 + 1, i3 = ss + ((i + 1) % segs) * 2 + 1;
        idx.push_back(i0); idx.push_back(i1); idx.push_back(i2);
        idx.push_back(i2); idx.push_back(i1); idx.push_back(i3);
    }
    setupBuffers(verts, idx);
}

void Mesh::generateTorus(float majorR, float minorR, int majorSegs, int minorSegs) {
    std::vector<Vertex> verts;
    std::vector<unsigned int> idx;
    for (int i = 0; i <= majorSegs; i++) {
        float u = (float)i / majorSegs * 2 * 3.14159f;
        for (int j = 0; j <= minorSegs; j++) {
            float v = (float)j / minorSegs * 2 * 3.14159f;
            Vertex vt;
            vt.position = {
                (majorR + minorR * std::cos(v)) * std::cos(u),
                minorR * std::sin(v),
                (majorR + minorR * std::cos(v)) * std::sin(u)
            };
            float du = -std::sin(u), dv = std::cos(u);
            vt.normal = {std::cos(v) * std::cos(u), std::sin(v), std::cos(v) * std::sin(u)};
            vt.texCoord = {(float)i / majorSegs, (float)j / minorSegs};
            vt.tangent = {du, 0, dv};
            vt.bitangent = glm::cross(vt.normal, vt.tangent);
            verts.push_back(vt);
        }
    }
    for (int i = 0; i < majorSegs; i++) {
        for (int j = 0; j < minorSegs; j++) {
            int i0 = i * (minorSegs + 1) + j;
            int i1 = i0 + 1;
            int i2 = i0 + (minorSegs + 1);
            int i3 = i2 + 1;
            idx.push_back(i0); idx.push_back(i2); idx.push_back(i1);
            idx.push_back(i1); idx.push_back(i2); idx.push_back(i3);
        }
    }
    setupBuffers(verts, idx);
}

void Mesh::bind() const { glBindVertexArray(m_vao); }
void Mesh::unbind() const { glBindVertexArray(0); }

} // namespace fc
''')

    # Framebuffer
    write_file(BASE_DIR / 'src/renderer/Framebuffer.hpp', r'''#pragma once
#include <glad/glad.h>

namespace fc {
class Framebuffer {
public:
    enum Flags { Color = 1, Depth = 2, GBuffer = 4, HDR = 8, DepthOnly = 16 };
    Framebuffer(int w, int h, int flags);
    ~Framebuffer();
    void bind();
    void unbind();
    void bindTextures();
    void resize(int w, int h);
    GLuint getColorTexture() const { return m_color; }
    GLuint getDepthTexture() const { return m_depth; }
    GLuint getPositionTexture() const { return m_pos; }
    GLuint getNormalTexture() const { return m_norm; }
    GLuint getAlbedoTexture() const { return m_albedo; }
private:
    GLuint m_fbo = 0;
    int m_w, m_h, m_flags;
    GLuint m_color = 0, m_depth = 0, m_pos = 0, m_norm = 0, m_albedo = 0, m_material = 0, m_rbo = 0;
    void create();
    void destroy();
};
} // namespace fc
''')

    write_file(BASE_DIR / 'src/renderer/Framebuffer.cpp', r'''#include "Framebuffer.hpp"
#include <iostream>

namespace fc {

Framebuffer::Framebuffer(int w, int h, int flags) : m_w(w), m_h(h), m_flags(flags) {
    create();
}

Framebuffer::~Framebuffer() {
    destroy();
}

void Framebuffer::create() {
    glGenFramebuffers(1, &m_fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, m_fbo);

    if (m_flags & GBuffer) {
        // Position
        glGenTextures(1, &m_pos);
        glBindTexture(GL_TEXTURE_2D, m_pos);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, m_w, m_h, 0, GL_RGBA, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, m_pos, 0);

        // Normal
        glGenTextures(1, &m_norm);
        glBindTexture(GL_TEXTURE_2D, m_norm);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, m_w, m_h, 0, GL_RGBA, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, m_norm, 0);

        // Albedo
        glGenTextures(1, &m_albedo);
        glBindTexture(GL_TEXTURE_2D, m_albedo);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, m_w, m_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, m_albedo, 0);

        // Material (metallic, roughness, ao, emissive)
        glGenTextures(1, &m_material);
        glBindTexture(GL_TEXTURE_2D, m_material);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, m_w, m_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT3, GL_TEXTURE_2D, m_material, 0);

        GLuint attachments[] = {GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2, GL_COLOR_ATTACHMENT3};
        glDrawBuffers(4, attachments);
    } else if (m_flags & HDR) {
        glGenTextures(1, &m_color);
        glBindTexture(GL_TEXTURE_2D, m_color);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, m_w, m_h, 0, GL_RGBA, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, m_color, 0);
    } else if (m_flags & DepthOnly) {
        // Depth-only (shadow map)
        glGenTextures(1, &m_depth);
        glBindTexture(GL_TEXTURE_2D, m_depth);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, m_w, m_h, 0, GL_DEPTH_COMPONENT, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
        float border[] = {1,1,1,1};
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, m_depth, 0);
        glDrawBuffer(GL_NONE);
        glReadBuffer(GL_NONE);
    } else {
        glGenTextures(1, &m_color);
        glBindTexture(GL_TEXTURE_2D, m_color);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, m_w, m_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, m_color, 0);
    }

    if ((m_flags & Depth) || (m_flags & GBuffer) || (m_flags & HDR)) {
        glGenRenderbuffers(1, &m_rbo);
        glBindRenderbuffer(GL_RENDERBUFFER, m_rbo);
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, m_w, m_h);
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, m_rbo);
    }

    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        std::cerr << "[Framebuffer] Incomplete!\n";
    }

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void Framebuffer::destroy() {
    if (m_fbo) glDeleteFramebuffers(1, &m_fbo);
    if (m_color) glDeleteTextures(1, &m_color);
    if (m_depth) glDeleteTextures(1, &m_depth);
    if (m_pos) glDeleteTextures(1, &m_pos);
    if (m_norm) glDeleteTextures(1, &m_norm);
    if (m_albedo) glDeleteTextures(1, &m_albedo);
    if (m_material) glDeleteTextures(1, &m_material);
    if (m_rbo) glDeleteRenderbuffers(1, &m_rbo);
}

void Framebuffer::bind() {
    glBindFramebuffer(GL_FRAMEBUFFER, m_fbo);
    glViewport(0, 0, m_w, m_h);
}

void Framebuffer::unbind() {
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void Framebuffer::bindTextures() {
    if (m_pos) {
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, m_pos);
    }
    if (m_norm) {
        glActiveTexture(GL_TEXTURE1);
        glBindTexture(GL_TEXTURE_2D, m_norm);
    }
    if (m_albedo) {
        glActiveTexture(GL_TEXTURE2);
        glBindTexture(GL_TEXTURE_2D, m_albedo);
    }
    if (m_material) {
        glActiveTexture(GL_TEXTURE3);
        glBindTexture(GL_TEXTURE_2D, m_material);
    }
}

void Framebuffer::resize(int w, int h) {
    destroy();
    m_w = w; m_h = h;
    create();
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 4. PHYSICS
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/physics/PhysicsEngine.hpp', r'''#pragma once
#include <vector>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

namespace fc {

struct RigidBody {
    glm::vec3 position{0,0,0};
    glm::vec3 velocity{0,0,0};
    glm::vec3 acceleration{0,0,0};
    glm::quat rotation{1,0,0,0};
    glm::vec3 angularVelocity{0,0,0};
    float mass = 1.0f, invMass = 1.0f;
    float restitution = 0.3f, friction = 0.5f;
    float drag = 0.01f, angularDrag = 0.05f;
    bool isKinematic = false, useGravity = true;
    glm::vec3 force{0,0,0}, torque{0,0,0};
    void applyForce(const glm::vec3& f);
    void applyForceAtPoint(const glm::vec3& f, const glm::vec3& p);
    void applyTorque(const glm::vec3& t);
    void applyImpulse(const glm::vec3& imp);
    glm::vec3 getForward() const;
    glm::vec3 getRight() const;
    glm::vec3 getUp() const;
};

struct Collider {
    enum Type { Sphere, Box, Capsule, Mesh } type;
    glm::vec3 offset{0,0,0};
    glm::vec3 halfExtents{1,1,1};
    float radius = 1.0f;
};

struct RaycastHit {
    int bodyId = -1;
    glm::vec3 point, normal;
    float distance = 0;
    bool hit = false;
};

class PhysicsEngine {
public:
    PhysicsEngine();
    ~PhysicsEngine();
    void step(float dt);
    void setGravity(const glm::vec3& g) { m_gravity = g; }
    int addBody(const RigidBody& body);
    int addCollider(int bodyId, const Collider& col);
    void setBodyPosition(int id, const glm::vec3& p);
    void setBodyVelocity(int id, const glm::vec3& v);
    void setBodyRotation(int id, const glm::quat& q);
    void applyForce(int id, const glm::vec3& f);
    void applyTorque(int id, const glm::vec3& t);
    RigidBody& getBody(int id);
    const RigidBody& getBody(int id) const;
    RaycastHit raycast(const glm::vec3& origin, const glm::vec3& dir, float maxDist);
    void setSubsteps(int s) { m_substeps = s; }
    int getBodyCount() const { return (int)m_bodies.size(); }
private:
    std::vector<RigidBody> m_bodies;
    std::vector<std::vector<Collider>> m_colliders;
    glm::vec3 m_gravity{0, -9.81f, 0};
    int m_substeps = 4;
    void integrate(float dt);
    void solveCollisions();
    void solveConstraints();
    bool sphereSphere(int a, int b, glm::vec3& normal, float& depth);
    bool sphereBox(int a, int b, glm::vec3& normal, float& depth);
    bool boxBox(int a, int b, glm::vec3& normal, float& depth);
    void resolveCollision(int a, int b, const glm::vec3& normal, float depth);
};

} // namespace fc
''')

    write_file(BASE_DIR / 'src/physics/PhysicsEngine.cpp', r'''#include "PhysicsEngine.hpp"
#include <algorithm>
#include <cmath>

namespace fc {

void RigidBody::applyForce(const glm::vec3& f) { force += f; }
void RigidBody::applyForceAtPoint(const glm::vec3& f, const glm::vec3& p) {
    force += f;
    torque += glm::cross(p - position, f);
}
void RigidBody::applyTorque(const glm::vec3& t) { torque += t; }
void RigidBody::applyImpulse(const glm::vec3& imp) {
    if (!isKinematic) velocity += imp * invMass;
}
glm::vec3 RigidBody::getForward() const {
    return rotation * glm::vec3(0, 0, -1);
}
glm::vec3 RigidBody::getRight() const {
    return rotation * glm::vec3(1, 0, 0);
}
glm::vec3 RigidBody::getUp() const {
    return rotation * glm::vec3(0, 1, 0);
}

PhysicsEngine::PhysicsEngine() = default;
PhysicsEngine::~PhysicsEngine() = default;

void PhysicsEngine::step(float dt) {
    float subDt = dt / m_substeps;
    for (int s = 0; s < m_substeps; s++) {
        integrate(subDt);
        solveCollisions();
        solveConstraints();
    }
}

void PhysicsEngine::integrate(float dt) {
    for (auto& b : m_bodies) {
        if (b.isKinematic) continue;
        if (b.useGravity) b.force += b.mass * m_gravity;
        b.acceleration = b.force * b.invMass;
        b.velocity += b.acceleration * dt;
        b.velocity *= (1.0f - b.drag * dt);
        b.position += b.velocity * dt;
        b.angularVelocity += b.torque * dt;
        b.angularVelocity *= (1.0f - b.angularDrag * dt);
        glm::quat dq(0, b.angularVelocity.x * 0.5f * dt, b.angularVelocity.y * 0.5f * dt, b.angularVelocity.z * 0.5f * dt);
        b.rotation = glm::normalize(b.rotation + dq * b.rotation);
        b.force = glm::vec3(0);
        b.torque = glm::vec3(0);
    }
}

void PhysicsEngine::solveCollisions() {
    for (size_t i = 0; i < m_bodies.size(); i++) {
        for (size_t j = i + 1; j < m_bodies.size(); j++) {
            for (const auto& ci : m_colliders[i]) {
                for (const auto& cj : m_colliders[j]) {
                    glm::vec3 normal;
                    float depth;
                    bool hit = false;
                    if (ci.type == Collider::Sphere && cj.type == Collider::Sphere)
                        hit = sphereSphere(i, j, normal, depth);
                    else if (ci.type == Collider::Sphere && cj.type == Collider::Box)
                        hit = sphereBox(i, j, normal, depth);
                    else if (ci.type == Collider::Box && cj.type == Collider::Sphere)
                        { hit = sphereBox(j, i, normal, depth); normal = -normal; }
                    else if (ci.type == Collider::Box && cj.type == Collider::Box)
                        hit = boxBox(i, j, normal, depth);
                    if (hit && depth > 0) resolveCollision(i, j, normal, depth);
                }
            }
        }
    }
}

void PhysicsEngine::resolveCollision(int a, int b, const glm::vec3& normal, float depth) {
    auto& ba = m_bodies[a];
    auto& bb = m_bodies[b];
    float totalInvMass = ba.invMass + bb.invMass;
    if (totalInvMass > 0) {
        glm::vec3 corr = normal * depth / totalInvMass;
        if (!ba.isKinematic) ba.position += corr * ba.invMass;
        if (!bb.isKinematic) bb.position -= corr * bb.invMass;
    }
    glm::vec3 relVel = bb.velocity - ba.velocity;
    float velAlong = glm::dot(relVel, normal);
    if (velAlong > 0) return;
    float e = std::min(ba.restitution, bb.restitution);
    float j = -(1 + e) * velAlong / totalInvMass;
    glm::vec3 impulse = j * normal;
    if (!ba.isKinematic) ba.applyImpulse(-impulse);
    if (!bb.isKinematic) bb.applyImpulse(impulse);
    // Friction
    relVel = bb.velocity - ba.velocity;
    glm::vec3 tangent = relVel - normal * velAlong;
    if (glm::length(tangent) > 0.001f) {
        tangent = glm::normalize(tangent);
        float jt = -glm::dot(relVel, tangent) / totalInvMass;
        float mu = std::sqrt(ba.friction * ba.friction + bb.friction * bb.friction);
        glm::vec3 fImpulse = tangent * std::clamp(jt, -mu * j, mu * j);
        if (!ba.isKinematic) ba.applyImpulse(-fImpulse);
        if (!bb.isKinematic) bb.applyImpulse(fImpulse);
    }
}

void PhysicsEngine::solveConstraints() {
    for (auto& b : m_bodies) {
        if (b.position.y < 0 && !b.isKinematic) {
            b.position.y = 0;
            if (b.velocity.y < 0) b.velocity.y *= -b.restitution;
        }
    }
}

int PhysicsEngine::addBody(const RigidBody& body) {
    m_bodies.push_back(body);
    m_colliders.emplace_back();
    return (int)m_bodies.size() - 1;
}

int PhysicsEngine::addCollider(int bodyId, const Collider& col) {
    if (bodyId >= 0 && bodyId < (int)m_colliders.size()) {
        m_colliders[bodyId].push_back(col);
        return (int)m_colliders[bodyId].size() - 1;
    }
    return -1;
}

void PhysicsEngine::setBodyPosition(int id, const glm::vec3& p) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].position = p;
}

void PhysicsEngine::setBodyVelocity(int id, const glm::vec3& v) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].velocity = v;
}

void PhysicsEngine::setBodyRotation(int id, const glm::quat& q) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].rotation = q;
}

void PhysicsEngine::applyForce(int id, const glm::vec3& f) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].applyForce(f);
}

void PhysicsEngine::applyTorque(int id, const glm::vec3& t) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].applyTorque(t);
}

RigidBody& PhysicsEngine::getBody(int id) { return m_bodies[id]; }
const RigidBody& PhysicsEngine::getBody(int id) const { return m_bodies[id]; }

RaycastHit PhysicsEngine::raycast(const glm::vec3& origin, const glm::vec3& dir, float maxDist) {
    RaycastHit result;
    result.distance = maxDist;
    for (size_t i = 0; i < m_bodies.size(); i++) {
        for (const auto& col : m_colliders[i]) {
            if (col.type == Collider::Sphere) {
                glm::vec3 oc = origin - (m_bodies[i].position + col.offset);
                float b = glm::dot(oc, dir);
                float c = glm::dot(oc, oc) - col.radius * col.radius;
                float disc = b * b - c;
                if (disc > 0) {
                    float dist = -b - std::sqrt(disc);
                    if (dist > 0 && dist < result.distance) {
                        result.hit = true;
                        result.distance = dist;
                        result.bodyId = (int)i;
                        result.point = origin + dir * dist;
                        result.normal = glm::normalize(result.point - (m_bodies[i].position + col.offset));
                    }
                }
            }
        }
    }
    return result;
}

bool PhysicsEngine::sphereSphere(int a, int b, glm::vec3& normal, float& depth) {
    glm::vec3 diff = (m_bodies[b].position + m_colliders[b][0].offset) - (m_bodies[a].position + m_colliders[a][0].offset);
    float dist = glm::length(diff);
    float minD = m_colliders[a][0].radius + m_colliders[b][0].radius;
    if (dist < minD && dist > 0) {
        normal = -diff / dist;
        depth = minD - dist;
        return true;
    }
    return false;
}

bool PhysicsEngine::sphereBox(int a, int b, glm::vec3& normal, float& depth) {
    glm::vec3 spherePos = m_bodies[a].position + m_colliders[a][0].offset;
    glm::vec3 boxPos = m_bodies[b].position + m_colliders[b][0].offset;
    glm::vec3 closest = glm::clamp(spherePos - boxPos, -m_colliders[b][0].halfExtents, m_colliders[b][0].halfExtents);
    glm::vec3 diff = (spherePos - boxPos) - closest;
    float dist = glm::length(diff);
    if (dist < m_colliders[a][0].radius && dist > 0) {
        normal = -diff / dist;
        depth = m_colliders[a][0].radius - dist;
        return true;
    }
    return false;
}

bool PhysicsEngine::boxBox(int a, int b, glm::vec3& normal, float& depth) {
    glm::vec3 posA = m_bodies[a].position + m_colliders[a][0].offset;
    glm::vec3 posB = m_bodies[b].position + m_colliders[b][0].offset;
    glm::vec3 minA = posA - m_colliders[a][0].halfExtents;
    glm::vec3 maxA = posA + m_colliders[a][0].halfExtents;
    glm::vec3 minB = posB - m_colliders[b][0].halfExtents;
    glm::vec3 maxB = posB + m_colliders[b][0].halfExtents;
    if (maxA.x < minB.x || minA.x > maxB.x) return false;
    if (maxA.y < minB.y || minA.y > maxB.y) return false;
    if (maxA.z < minB.z || minA.z > maxB.z) return false;
    float overlaps[6] = {
        maxA.x - minB.x, maxB.x - minA.x,
        maxA.y - minB.y, maxB.y - minA.y,
        maxA.z - minB.z, maxB.z - minA.z
    };
    float minO = overlaps[0];
    int axis = 0;
    for (int i = 1; i < 6; i++) if (overlaps[i] < minO) { minO = overlaps[i]; axis = i; }
    static const glm::vec3 axes[] = {{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
    normal = axes[axis];
    depth = minO;
    return true;
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 5. AUDIO (stub, ready for OpenAL/miniaudio)
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/audio/AudioEngine.hpp', r'''#pragma once
#include <string>
#include <vector>
#include <glm/glm.hpp>

namespace fc {
struct AudioSource {
    unsigned int id = 0;
    glm::vec3 position;
    float volume = 1.0f, pitch = 1.0f;
    bool loop = false, is3D = true;
    float minDist = 1.0f, maxDist = 100.0f;
};
class AudioEngine {
public:
    AudioEngine();
    ~AudioEngine();
    bool initialize();
    void shutdown();
    void update();
    int loadSound(const std::string& path);
    void playSound(int id, const glm::vec3& pos = glm::vec3(0));
    void playMusic(const std::string& path, float vol = 0.5f);
    void stopMusic();
    void setListener(const glm::vec3& pos, const glm::vec3& fwd, const glm::vec3& up);
    void setMasterVolume(float v);
private:
    void* m_device = nullptr;
    std::vector<void*> m_sounds;
    void* m_music = nullptr;
    float m_masterVol = 1.0f;
};
} // namespace fc
''')

    write_file(BASE_DIR / 'src/audio/AudioEngine.cpp', r'''#include "AudioEngine.hpp"
#include <iostream>

namespace fc {

AudioEngine::AudioEngine() = default;
AudioEngine::~AudioEngine() { shutdown(); }

bool AudioEngine::initialize() {
    std::cout << "[Audio] Engine initialized (stub - integrate OpenAL/miniaudio here)\n";
    return true;
}

void AudioEngine::shutdown() {
    std::cout << "[Audio] Engine shutdown\n";
}

void AudioEngine::update() {
    // Update 3D audio positions
}

int AudioEngine::loadSound(const std::string& path) {
    m_sounds.push_back(nullptr);
    return (int)m_sounds.size() - 1;
}

void AudioEngine::playSound(int id, const glm::vec3& pos) {
    // Play sound at position
}

void AudioEngine::playMusic(const std::string& path, float vol) {
    std::cout << "[Audio] Playing music: " << path << " at volume " << vol << "\n";
}

void AudioEngine::stopMusic() {
    // Stop music
}

void AudioEngine::setListener(const glm::vec3& pos, const glm::vec3& fwd, const glm::vec3& up) {
    // Update listener position/orientation
}

void AudioEngine::setMasterVolume(float v) {
    m_masterVol = v;
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 6. GAME INTERFACE
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/game/IGame.hpp', r'''#pragma once
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
''')

    # ═══════════════════════════════════════════════════════════════════
    # 7. FORZA GAME - THE MAIN GAME CLASS
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/game/ForzaGame.hpp', r'''#pragma once
#include "IGame.hpp"
#include <memory>
#include <vector>
#include <string>
#include <glm/glm.hpp>
#include "../renderer/Camera.hpp"
#include "../renderer/Mesh.hpp"
#include "../physics/PhysicsEngine.hpp"

namespace fc {

class Terrain;
class Skybox;
class Car;
class ParticleSystem;
class RoadNetwork;
class BuildingGenerator;

struct InputState {
    bool throttle = false;
    bool brake = false;
    bool reverse = false;
    bool left = false;
    bool right = false;
    bool handbrake = false;
    bool reset = false;
    bool lookLeft = false;
    bool lookRight = false;
    bool lookBack = false;
    bool pause = false;
    float mouseX = 0, mouseY = 0;
    bool mouseCaptured = true;
};

class ForzaGame : public IGame {
public:
    ForzaGame();
    ~ForzaGame();
    
    void initialize(GameEngine* engine) override;
    void shutdown() override;
    void processInput(GLFWwindow* window, float dt) override;
    void update(float dt) override;
    void render(RenderEngine* renderer) override;
    void onWindowResize(int width, int height) override;
    
private:
    GameEngine* m_engine = nullptr;
    
    std::unique_ptr<Camera> m_camera;
    std::unique_ptr<Terrain> m_terrain;
    std::unique_ptr<Skybox> m_skybox;
    std::unique_ptr<Car> m_car;
    std::unique_ptr<ParticleSystem> m_particles;
    std::unique_ptr<RoadNetwork> m_roads;
    std::unique_ptr<BuildingGenerator> m_buildings;
    
    InputState m_input;
    PhysicsEngine m_physics;
    
    // Car physics body
    int m_carBodyId = -1;
    int m_carColliderId = -1;
    
    // Camera modes
    enum CamMode { Chase, Hood, Bumper, Drone, Cinematic };
    CamMode m_camMode = Chase;
    float m_camYaw = 0, m_camPitch = 0.3f;
    float m_camDistance = 12.0f;
    float m_camHeight = 3.0f;
    
    // HUD
    struct HUDState {
        float speed = 0;
        float rpm = 0;
        int gear = 1;
        float throttle = 0;
        float brake = 0;
        std::string surface = "OFF-ROAD";
        float lapTime = 0;
        int position = 1;
    } m_hud;
    
    // World
    glm::vec3 m_sunDir{0.3f, -0.8f, 0.5f};
    glm::vec3 m_sunColor{1.0f, 0.95f, 0.8f};
    float m_timeOfDay = 12.0f;
    
    void updateCamera(float dt);
    void updateCarPhysics(float dt);
    void updateHUD(float dt);
    void updateTimeOfDay(float dt);
    void renderHUD();
    
    void setupWorld();
    void setupCar();
    void setupRoads();
    void setupBuildings();
    
    float getTerrainHeight(float x, float z) const;
    glm::vec3 getTerrainNormal(float x, float z) const;
};

} // namespace fc
''')

    write_file(BASE_DIR / 'src/game/ForzaGame.cpp', r'''#include "ForzaGame.hpp"
#include <iostream>
#include <cmath>
#include <cstdlib>
#include <GLFW/glfw3.h>
#include "../engine/GameEngine.hpp"
#include "../renderer/RenderEngine.hpp"
#include "Terrain.hpp"
#include "Skybox.hpp"
#include "Car.hpp"
#include "ParticleSystem.hpp"
#include "RoadNetwork.hpp"
#include "BuildingGenerator.hpp"

namespace fc {

ForzaGame::ForzaGame() = default;
ForzaGame::~ForzaGame() = default;

void ForzaGame::initialize(GameEngine* engine) {
    m_engine = engine;
    std::cout << "[Game] Initializing Forza Cubey World...\n";
    
    int w, h;
    glfwGetWindowSize(engine->getWindow(), &w, &h);
    
    m_camera = std::make_unique<Camera>(70.0f, (float)w/h, 0.1f, 5000.0f);
    
    setupWorld();
    setupCar();
    setupRoads();
    setupBuildings();
    
    m_skybox = std::make_unique<Skybox>();
    m_particles = std::make_unique<ParticleSystem>(10000);
    
    m_physics.setGravity(glm::vec3(0, -15.0f, 0));
    
    std::cout << "[Game] Initialization complete!\n";
}

void ForzaGame::shutdown() {
    std::cout << "[Game] Shutting down...\n";
}

void ForzaGame::processInput(GLFWwindow* window, float dt) {
    m_input.throttle = glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS || 
                       glfwGetKey(window, GLFW_KEY_UP) == GLFW_PRESS;
    m_input.brake = glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS;
    m_input.reverse = glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS ||
                      glfwGetKey(window, GLFW_KEY_DOWN) == GLFW_PRESS;
    m_input.left = glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS ||
                   glfwGetKey(window, GLFW_KEY_LEFT) == GLFW_PRESS;
    m_input.right = glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS ||
                    glfwGetKey(window, GLFW_KEY_RIGHT) == GLFW_PRESS;
    m_input.handbrake = glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS;
    m_input.reset = glfwGetKey(window, GLFW_KEY_R) == GLFW_PRESS;
    m_input.lookLeft = glfwGetKey(window, GLFW_KEY_Q) == GLFW_PRESS;
    m_input.lookRight = glfwGetKey(window, GLFW_KEY_E) == GLFW_PRESS;
    m_input.lookBack = glfwGetKey(window, GLFW_KEY_C) == GLFW_PRESS;
    m_input.pause = glfwGetKey(window, GLFW_KEY_P) == GLFW_PRESS;
    
    if (glfwGetKey(window, GLFW_KEY_1) == GLFW_PRESS) m_camMode = Chase;
    if (glfwGetKey(window, GLFW_KEY_2) == GLFW_PRESS) m_camMode = Hood;
    if (glfwGetKey(window, GLFW_KEY_3) == GLFW_PRESS) m_camMode = Bumper;
    if (glfwGetKey(window, GLFW_KEY_4) == GLFW_PRESS) m_camMode = Drone;
    if (glfwGetKey(window, GLFW_KEY_5) == GLFW_PRESS) m_camMode = Cinematic;
    
    // Mouse look (only in chase/drone mode)
    if (m_camMode == Chase || m_camMode == Drone) {
        if (m_input.mouseCaptured) {
            double mx, my;
            glfwGetCursorPos(window, &mx, &my);
            float dx = (float)(mx - m_input.mouseX) * 0.005f;
            float dy = (float)(my - m_input.mouseY) * 0.005f;
            m_camYaw -= dx;
            m_camPitch += dy;
            m_camPitch = glm::clamp(m_camPitch, -1.5f, 1.5f);
            m_input.mouseX = mx;
            m_input.mouseY = my;
        }
    }
    
    if (m_input.reset) {
        auto& body = m_physics.getBody(m_carBodyId);
        body.position = glm::vec3(0, getTerrainHeight(0, 0) + 1.0f, 0);
        body.velocity = glm::vec3(0);
        body.rotation = glm::quat(1, 0, 0, 0);
        body.angularVelocity = glm::vec3(0);
    }
}

void ForzaGame::update(float dt) {
    updateCarPhysics(dt);
    updateCamera(dt);
    updateHUD(dt);
    updateTimeOfDay(dt);
    
    m_physics.step(dt);
    m_particles->update(dt);
    
    // Update car visual from physics
    if (m_carBodyId >= 0) {
        auto& body = m_physics.getBody(m_carBodyId);
        m_car->setPosition(body.position);
        m_car->setRotation(body.rotation);
    }
}

void ForzaGame::render(RenderEngine* renderer) {
    // Set lighting
    DirectionalLight light;
    light.direction = m_sunDir;
    light.color = m_sunColor;
    light.intensity = 2.5f;
    renderer->setLight(light);
    
    // Skybox
    renderer->renderSkybox(*m_skybox, *m_camera);
    
    // Terrain
    renderer->renderTerrain(*m_terrain, *m_camera);
    
    // Roads
    m_roads->render(*renderer, *m_camera);
    
    // Buildings
    m_buildings->render(*renderer, *m_camera);
    
    // Car
    renderer->renderCar(*m_car, *m_camera);
    
    // Particles
    renderer->renderParticles(m_particles->getParticles());
    
    // HUD
    renderHUD();
}

void ForzaGame::onWindowResize(int width, int height) {
    // Handle resize
}

void ForzaGame::setupWorld() {
    m_terrain = std::make_unique<Terrain>(5000.0f, 250);
}

void ForzaGame::setupCar() {
    m_car = std::make_unique<Car>();
    
    // Create physics body
    RigidBody body;
    body.position = glm::vec3(0, getTerrainHeight(0, 0) + 1.0f, 0);
    body.mass = 1200.0f;
    body.invMass = 1.0f / body.mass;
    body.restitution = 0.2f;
    body.friction = 0.8f;
    body.drag = 0.02f;
    body.angularDrag = 0.1f;
    
    m_carBodyId = m_physics.addBody(body);
    
    // Car collider (box)
    Collider collider;
    collider.type = Collider::Box;
    collider.halfExtents = glm::vec3(1.0f, 0.5f, 2.2f);
    collider.offset = glm::vec3(0, 0.5f, 0);
    m_carColliderId = m_physics.addCollider(m_carBodyId, collider);
    
    // Wheel colliders
    Collider wheelCol;
    wheelCol.type = Collider::Sphere;
    wheelCol.radius = 0.35f;
    wheelCol.offset = glm::vec3(-1.05f, 0.35f, -1.3f);
    m_physics.addCollider(m_carBodyId, wheelCol);
    wheelCol.offset = glm::vec3(1.05f, 0.35f, -1.3f);
    m_physics.addCollider(m_carBodyId, wheelCol);
    wheelCol.offset = glm::vec3(-1.05f, 0.35f, 1.3f);
    m_physics.addCollider(m_carBodyId, wheelCol);
    wheelCol.offset = glm::vec3(1.05f, 0.35f, 1.3f);
    m_physics.addCollider(m_carBodyId, wheelCol);
}

void ForzaGame::setupRoads() {
    m_roads = std::make_unique<RoadNetwork>();
    m_roads->generateRoads();
}

void ForzaGame::setupBuildings() {
    m_buildings = std::make_unique<BuildingGenerator>();
    m_buildings->generateBuildings();
}

void ForzaGame::updateCamera(float dt) {
    if (!m_car) return;
    
    auto& body = m_physics.getBody(m_carBodyId);
    glm::vec3 carPos = body.position;
    glm::vec3 carForward = body.getForward();
    
    float targetDist = m_camDistance;
    float targetHeight = m_camHeight;
    float lag = 3.0f;
    
    switch (m_camMode) {
        case Chase:
            targetDist = 12.0f;
            targetHeight = 3.0f;
            break;
        case Hood:
            targetDist = 0.5f;
            targetHeight = 1.2f;
            lag = 15.0f;
            m_camYaw = 0;
            m_camPitch = 0;
            break;
        case Bumper:
            targetDist = -2.5f;
            targetHeight = 0.8f;
            lag = 15.0f;
            m_camYaw = 0;
            m_camPitch = 0;
            break;
        case Drone:
            targetDist = 30.0f;
            targetHeight = 20.0f;
            lag = 1.0f;
            break;
        case Cinematic:
            targetDist = 8.0f;
            targetHeight = 2.0f;
            lag = 5.0f;
            // Auto-rotate
            m_camYaw += dt * 0.2f;
            break;
    }
    
    // Speed-based FOV
    float speed = glm::length(body.velocity) * 3.6f; // km/h
    float targetFOV = 70.0f + glm::clamp(speed / 200.0f, 0.0f, 1.0f) * 20.0f;
    float currentFOV = m_camera->getFOV();
    m_camera->setFOV(currentFOV + (targetFOV - currentFOV) * dt * 5.0f);
    
    // Camera shake at high speed
    glm::vec3 shake(0);
    if (speed > 150.0f) {
        float shakeAmount = (speed - 150.0f) / 150.0f * 0.03f;
        shake.x = (rand() / (float)RAND_MAX - 0.5f) * shakeAmount;
        shake.y = (rand() / (float)RAND_MAX - 0.5f) * shakeAmount;
    }
    
    m_camera->follow(carPos, targetDist, targetHeight, m_camYaw, m_camPitch, lag, dt);
    
    // Add shake
    if (speed > 150.0f) {
        auto pos = m_camera->getPosition();
        m_camera->setPosition(pos + shake);
    }
}

void ForzaGame::updateCarPhysics(float dt) {
    if (m_carBodyId < 0) return;
    
    auto& body = m_physics.getBody(m_carBodyId);
    
    // Get road type at current position
    std::string roadType = m_roads->getRoadType(body.position.x, body.position.z);
    
    // Physics params based on surface
    float maxSpeed = 90.0f; // m/s ~= 324 km/h
    float accel = 30.0f;
    float brakeForce = 60.0f;
    float friction = 0.8f;
    float turnSpeed = 2.5f;
    
    if (roadType == "highway") {
        maxSpeed = 90.0f;
        friction = 0.9f;
    } else if (roadType == "street") {
        maxSpeed = 72.0f;
        friction = 0.85f;
    } else if (roadType == "dirt") {
        maxSpeed = 40.0f;
        friction = 0.5f;
        accel = 20.0f;
        turnSpeed = 1.5f;
    } else {
        // Off-road
        maxSpeed = 50.0f;
        friction = 0.4f;
        accel = 15.0f;
        turnSpeed = 1.2f;
    }
    
    // Apply handbrake
    if (m_input.handbrake) {
        friction *= 0.3f;
        // Drift physics
    }
    
    // Throttle
    if (m_input.throttle) {
        glm::vec3 forward = body.getForward();
        float currentSpeed = glm::dot(body.velocity, forward);
        if (currentSpeed < maxSpeed) {
            body.applyForce(forward * accel * body.mass);
        }
    }
    
    // Brake/Reverse
    if (m_input.brake) {
        glm::vec3 forward = body.getForward();
        float currentSpeed = glm::dot(body.velocity, forward);
        if (currentSpeed > 0.5f) {
            // Braking
            body.applyForce(-forward * brakeForce * body.mass);
        } else {
            // Reverse
            body.applyForce(-forward * accel * 0.5f * body.mass);
        }
    }
    
    // Steering
    if (m_input.left || m_input.right) {
        float steer = m_input.left ? 1.0f : -1.0f;
        float speed = glm::length(body.velocity);
        float steerFactor = glm::clamp(speed / 20.0f, 0.0f, 1.0f);
        
        // Apply steering torque
        glm::vec3 up = body.getUp();
        body.applyTorque(up * steer * turnSpeed * steerFactor * body.mass);
        
        // Counter-steer at low speed
        if (speed < 5.0f) {
            glm::vec3 forward = body.getForward();
            body.applyForce(forward * steer * 5.0f * body.mass);
        }
    }
    
    // Apply surface friction
    glm::vec3 vel = body.velocity;
    glm::vec3 forward = body.getForward();
    glm::vec3 right = body.getRight();
    
    float fwdSpeed = glm::dot(vel, forward);
    float rightSpeed = glm::dot(vel, right);
    
    // Lateral friction (prevents sliding)
    body.applyForce(-right * rightSpeed * friction * body.mass * 5.0f);
    
    // Rolling resistance
    body.applyForce(-forward * fwdSpeed * 0.01f * body.mass);
    
    // Air resistance
    float airDrag = 0.001f * fwdSpeed * fwdSpeed;
    body.applyForce(-forward * airDrag * body.mass);
    
    // Gravity on slopes
    float terrainH = getTerrainHeight(body.position.x, body.position.z);
    float terrainHFront = getTerrainHeight(
        body.position.x + forward.x * 2.0f, 
        body.position.z + forward.z * 2.0f
    );
    float slope = (terrainHFront - terrainH) / 2.0f;
    body.applyForce(glm::vec3(0, -slope * 9.81f * body.mass, 0));
    
    // Keep car on terrain
    body.position.y = terrainH + 0.6f;
    
    // Particle effects
    float speed = glm::length(body.velocity);
    if (m_input.brake && speed > 15.0f) {
        // Tire smoke
        for (int i = 0; i < 2; i++) {
            glm::vec3 wheelPos = body.position + body.rotation * glm::vec3(
                i == 0 ? -1.05f : 1.05f, 0.1f, 1.3f
            );
            m_particles->spawn(wheelPos, glm::vec3(0, 1, 0), 0.5f, "smoke");
        }
    }
    
    if (roadType.empty() && speed > 5.0f) {
        // Dust off-road
        for (int i = 0; i < 2; i++) {
            glm::vec3 wheelPos = body.position + body.rotation * glm::vec3(
                (i == 0 ? -1.0f : 1.0f) * (rand() / (float)RAND_MAX), 
                0, 
                (rand() / (float)RAND_MAX - 0.5f) * 2.0f
            );
            m_particles->spawn(wheelPos, glm::vec3(0, 0.5f, 0), 0.6f, "dust");
        }
    }
    
    if (m_input.throttle && speed > 1.0f) {
        // Exhaust
        glm::vec3 exhaustPos = body.position + body.rotation * glm::vec3(0.55f, 0.3f, 2.2f);
        glm::vec3 exhaustVel = -forward * 2.0f + glm::vec3(0, 1, 0);
        m_particles->spawn(exhaustPos, exhaustVel, 0.5f, "smoke");
    }
}

void ForzaGame::updateHUD(float dt) {
    if (m_carBodyId < 0) return;
    
    auto& body = m_physics.getBody(m_carBodyId);
    float speed = glm::length(body.velocity) * 3.6f; // km/h
    
    m_hud.speed = speed;
    m_hud.throttle = m_input.throttle ? 1.0f : 0.0f;
    m_hud.brake = m_input.brake ? 1.0f : 0.0f;
    
    // Calculate gear and RPM
    float absSpeed = std::abs(speed);
    if (absSpeed < 0.5f) {
        m_hud.gear = 0; // Neutral
        m_hud.rpm = 850.0f + std::sin(glfwGetTime() * 5.0f) * 40.0f;
    } else if (speed < 0) {
        m_hud.gear = -1; // Reverse
        m_hud.rpm = 1500.0f + absSpeed / 25.0f * 3500.0f;
    } else {
        // Forward gears
        const float gearLimits[] = {0, 35, 65, 100, 140, 190, 250, 300};
        m_hud.gear = 1;
        for (int i = 1; i < 7; i++) {
            if (absSpeed > gearLimits[i]) m_hud.gear = i;
        }
        
        float prev = gearLimits[m_hud.gear - 1];
        float next = gearLimits[m_hud.gear];
        float ratio = (absSpeed - prev) / std::max(1.0f, next - prev);
        m_hud.rpm = 1500.0f + ratio * 5000.0f + m_hud.gear * 150.0f;
        m_hud.rpm = std::min(8000.0f, std::max(800.0f, m_hud.rpm));
    }
    
    m_hud.surface = m_roads->getRoadType(body.position.x, body.position.z);
    if (m_hud.surface.empty()) m_hud.surface = "OFF-ROAD";
    
    m_hud.lapTime += dt;
}

void ForzaGame::updateTimeOfDay(float dt) {
    // Optional: cycle time of day
    // m_timeOfDay += dt * 0.1f;
    // if (m_timeOfDay >= 24.0f) m_timeOfDay -= 24.0f;
    
    // Update sun direction based on time
    float angle = (m_timeOfDay - 6.0f) / 12.0f * 3.14159f; // 6am to 6pm
    m_sunDir.x = std::cos(angle) * 0.5f;
    m_sunDir.y = -std::sin(angle);
    m_sunDir.z = 0.3f;
    m_sunDir = glm::normalize(m_sunDir);
}

void ForzaGame::renderHUD() {
    // HUD rendering is done via ImGui or direct OpenGL
    // For now, this is a placeholder - integrate with your UI system
}

float ForzaGame::getTerrainHeight(float x, float z) const {
    if (m_terrain) return m_terrain->getHeight(x, z);
    return 0.0f;
}

glm::vec3 ForzaGame::getTerrainNormal(float x, float z) const {
    if (m_terrain) return m_terrain->getNormal(x, z);
    return glm::vec3(0, 1, 0);
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 8. TERRAIN
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/game/Terrain.hpp', r'''#pragma once
#include <vector>
#include <glm/glm.hpp>
#include "../renderer/Mesh.hpp"

namespace fc {

class RenderEngine;
class Camera;

class Terrain {
public:
    Terrain(float size, int segments);
    ~Terrain();
    
    void render(RenderEngine& renderer, const Camera& camera);
    float getHeight(float x, float z) const;
    glm::vec3 getNormal(float x, float z) const;
    
private:
    float m_size;
    int m_segments;
    Mesh m_mesh;
    
    // Noise functions
    float hash(float n) const;
    float noise2D(float x, float y) const;
    float fbm(float x, float y) const;
    
    void generateTerrain();
};

} // namespace fc
''')

    write_file(BASE_DIR / 'src/game/Terrain.cpp', r'''#include "Terrain.hpp"
#include <cmath>
#include "../renderer/RenderEngine.hpp"
#include "../renderer/Camera.hpp"

namespace fc {

Terrain::Terrain(float size, int segments) : m_size(size), m_segments(segments) {
    generateTerrain();
}

Terrain::~Terrain() = default;

void Terrain::generateTerrain() {
    std::vector<Vertex> vertices;
    std::vector<unsigned int> indices;
    
    float step = m_size / m_segments;
    float half = m_size / 2.0f;
    
    for (int z = 0; z <= m_segments; z++) {
        for (int x = 0; x <= m_segments; x++) {
            float wx = x * step - half;
            float wz = z * step - half;
            float h = getHeight(wx, wz);
            
            Vertex v;
            v.position = glm::vec3(wx, h, wz);
            v.normal = getNormal(wx, wz);
            v.texCoord = glm::vec2(x / (float)m_segments, z / (float)m_segments);
            v.tangent = glm::vec3(1, 0, 0);
            v.bitangent = glm::vec3(0, 0, 1);
            
            // Color based on height
            float t = glm::clamp(h / 60.0f, 0.0f, 1.0f);
            if (h < 2.0f) {
                v.color = glm::vec4(0.55f, 0.52f, 0.42f, 1.0f); // Sand
            } else if (h < 15.0f) {
                v.color = glm::vec4(0.22f + t * 0.1f, 0.35f + t * 0.2f, 0.15f + t * 0.05f, 1.0f); // Grass
            } else if (h < 50.0f) {
                v.color = glm::vec4(0.35f + t * 0.15f, 0.33f + t * 0.15f, 0.28f + t * 0.1f, 1.0f); // Rock
            } else {
                v.color = glm::vec4(0.7f + t * 0.2f, 0.7f + t * 0.2f, 0.72f + t * 0.2f, 1.0f); // Snow
            }
            
            vertices.push_back(v);
        }
    }
    
    for (int z = 0; z < m_segments; z++) {
        for (int x = 0; x < m_segments; x++) {
            int i0 = z * (m_segments + 1) + x;
            int i1 = i0 + 1;
            int i2 = i0 + (m_segments + 1);
            int i3 = i2 + 1;
            
            indices.push_back(i0);
            indices.push_back(i2);
            indices.push_back(i1);
            indices.push_back(i1);
            indices.push_back(i2);
            indices.push_back(i3);
        }
    }
    
    m_mesh.load(vertices, indices);
}

void Terrain::render(RenderEngine& renderer, const Camera& camera) {
    glm::mat4 model = glm::mat4(1.0f);
    renderer.renderMesh(m_mesh, model, renderer.getGeometryShader());
}

float Terrain::getHeight(float x, float z) const {
    float h = fbm(x * 0.0008f, z * 0.0008f) * 20.0f + 8.0f;
    h += fbm(x * 0.003f, z * 0.003f) * 6.0f;
    h += fbm(x * 0.008f, z * 0.008f) * 2.0f;
    
    // Mountain (Fuji-like)
    const float fujiX = 800.0f, fujiZ = -600.0f, fujiR = 500.0f, fujiH = 180.0f;
    float dFuji = std::sqrt((x - fujiX) * (x - fujiX) + (z - fujiZ) * (z - fujiZ));
    if (dFuji < fujiR) {
        float fh = fujiH * (1.0f - dFuji / fujiR);
        float bl = std::min(1.0f, (fujiR - dFuji) / 80.0f);
        h = std::max(h, fh * bl);
    }
    
    // Flatten center (city)
    float dc = std::sqrt(x * x + z * z);
    if (dc < 700.0f) h *= dc / 700.0f;
    
    // Flatten villages
    const glm::vec2 villages[] = {
        {-1400, -1000}, {1600, 700}, {-700, 1700}, {1900, -1500}, {-1700, 1300}
    };
    for (const auto& v : villages) {
        float d = std::sqrt((x - v.x) * (x - v.x) + (z - v.y) * (z - v.y));
        if (d < 300.0f) h *= d / 300.0f;
    }
    
    return std::max(0.0f, h);
}

glm::vec3 Terrain::getNormal(float x, float z) const {
    float eps = 2.0f;
    float hL = getHeight(x - eps, z);
    float hR = getHeight(x + eps, z);
    float hD = getHeight(x, z - eps);
    float hU = getHeight(x, z + eps);
    return glm::normalize(glm::vec3(hL - hR, 2.0f * eps, hD - hU));
}

float Terrain::hash(float n) const {
    float x = std::sin(n) * 43758.5453f;
    return x - std::floor(x);
}

float Terrain::noise2D(float x, float y) const {
    int xi = (int)std::floor(x);
    int yi = (int)std::floor(y);
    float xf = x - xi;
    float yf = y - yi;
    float u = xf * xf * (3.0f - 2.0f * xf);
    float v = yf * yf * (3.0f - 2.0f * yf);
    
    float a = hash(xi + yi * 157.0f);
    float b = hash(xi + 1 + yi * 157.0f);
    float c = hash(xi + (yi + 1) * 157.0f);
    float d = hash(xi + 1 + (yi + 1) * 157.0f);
    
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}

float Terrain::fbm(float x, float y) const {
    float v = 0.0f;
    float a = 1.0f;
    float f = 1.0f;
    for (int i = 0; i < 5; i++) {
        v += noise2D(x * f, y * f) * a;
        a *= 0.5f;
        f *= 2.0f;
    }
    return v;
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 9. SKYBOX
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/game/Skybox.hpp', r'''#pragma once
#include "../renderer/Mesh.hpp"

namespace fc {
class RenderEngine;
class Camera;
class Skybox {
public:
    Skybox();
    ~Skybox();
    void render(RenderEngine& renderer, const Camera& camera);
private:
    Mesh m_mesh;
};
} // namespace fc
''')

    write_file(BASE_DIR / 'src/game/Skybox.cpp', r'''#include "Skybox.hpp"
#include "../renderer/RenderEngine.hpp"
#include "../renderer/Camera.hpp"

namespace fc {

Skybox::Skybox() {
    m_mesh.generateSphere(1.0f, 32);
}

Skybox::~Skybox() = default;

void Skybox::render(RenderEngine& renderer, const Camera& camera) {
    // Render skybox with special shader (no depth write)
    glm::mat4 model = glm::mat4(1.0f);
    // renderer.renderSkyboxMesh(m_mesh, model);
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 10. CAR
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/game/Car.hpp', r'''#pragma once
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>
#include <vector>
#include <memory>
#include "../renderer/Mesh.hpp"

namespace fc {
class RenderEngine;
class Camera;

class Car {
public:
    Car();
    ~Car();
    
    void setPosition(const glm::vec3& pos);
    void setRotation(const glm::quat& rot);
    
    void render(RenderEngine& renderer, const Camera& camera);
    
    glm::vec3 getPosition() const { return m_position; }
    glm::quat getRotation() const { return m_rotation; }
    
private:
    glm::vec3 m_position{0, 0, 0};
    glm::quat m_rotation{1, 0, 0, 0};
    
    // Car parts
    Mesh m_chassis;
    Mesh m_cabin;
    Mesh m_wheel;
    Mesh m_spoiler;
    
    void generateCar();
};

} // namespace fc
''')

    write_file(BASE_DIR / 'src/game/Car.cpp', r'''#include "Car.hpp"
#include "../renderer/RenderEngine.hpp"
#include "../renderer/Camera.hpp"

namespace fc {

Car::Car() {
    generateCar();
}

Car::~Car() = default;

void Car::generateCar() {
    // Chassis
    m_chassis.generateCube(1.0f);
    // Cabin
    m_cabin.generateCube(0.8f);
    // Wheel
    m_wheel.generateCylinder(0.35f, 0.25f, 16);
    // Spoiler
    m_spoiler.generateCube(0.3f);
}

void Car::setPosition(const glm::vec3& pos) {
    m_position = pos;
}

void Car::setRotation(const glm::quat& rot) {
    m_rotation = rot;
}

void Car::render(RenderEngine& renderer, const Camera& camera) {
    glm::mat4 model = glm::translate(glm::mat4(1.0f), m_position);
    model *= glm::mat4_cast(m_rotation);
    
    // Render chassis
    glm::mat4 chassisMat = model;
    chassisMat = glm::scale(chassisMat, glm::vec3(2.0f, 0.65f, 4.2f));
    chassisMat = glm::translate(chassisMat, glm::vec3(0, 0.6f, 0));
    // renderer.renderMesh(m_chassis, chassisMat, carPaintShader);
    
    // Render cabin
    glm::mat4 cabinMat = model;
    cabinMat = glm::scale(cabinMat, glm::vec3(1.7f, 0.55f, 2.0f));
    cabinMat = glm::translate(cabinMat, glm::vec3(0, 1.2f, 0.3f));
    // renderer.renderMesh(m_cabin, cabinMat, glassShader);
    
    // Render wheels
    float wheelPositions[4][3] = {
        {-1.05f, 0.35f, -1.3f},
        {1.05f, 0.35f, -1.3f},
        {-1.05f, 0.35f, 1.3f},
        {1.05f, 0.35f, 1.3f}
    };
    
    for (int i = 0; i < 4; i++) {
        glm::mat4 wheelMat = model;
        wheelMat = glm::translate(wheelMat, glm::vec3(wheelPositions[i][0], wheelPositions[i][1], wheelPositions[i][2]));
        wheelMat = glm::rotate(wheelMat, glm::radians(90.0f), glm::vec3(0, 0, 1));
        // renderer.renderMesh(m_wheel, wheelMat, tireShader);
    }
    
    // Render spoiler
    glm::mat4 spoilerMat = model;
    spoilerMat = glm::scale(spoilerMat, glm::vec3(2.2f, 0.06f, 0.35f));
    spoilerMat = glm::translate(spoilerMat, glm::vec3(0, 1.12f, 1.85f));
    // renderer.renderMesh(m_spoiler, spoilerMat, carPaintShader);
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 11. PARTICLE SYSTEM
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/game/ParticleSystem.hpp', r'''#pragma once
#include <vector>
#include <glm/glm.hpp>
#include <string>

namespace fc {

struct Particle {
    glm::vec3 position;
    glm::vec3 velocity;
    float life;
    float maxLife;
    float size;
    std::string type;
};

class ParticleSystem {
public:
    ParticleSystem(int maxParticles);
    ~ParticleSystem();
    
    void update(float dt);
    void spawn(const glm::vec3& pos, const glm::vec3& vel, float life, const std::string& type);
    
    const std::vector<Particle>& getParticles() const { return m_particles; }
    
private:
    int m_maxParticles;
    std::vector<Particle> m_particles;
    int m_nextIndex = 0;
};

} // namespace fc
''')

    write_file(BASE_DIR / 'src/game/ParticleSystem.cpp', r'''#include "ParticleSystem.hpp"

namespace fc {

ParticleSystem::ParticleSystem(int maxParticles) : m_maxParticles(maxParticles) {
    m_particles.reserve(maxParticles);
}

ParticleSystem::~ParticleSystem() = default;

void ParticleSystem::update(float dt) {
    for (auto& p : m_particles) {
        if (p.life > 0) {
            p.position += p.velocity * dt;
            p.velocity.y += 0.5f * dt; // Rise
            p.life -= dt;
            p.size += dt * 0.5f; // Grow
        }
    }
}

void ParticleSystem::spawn(const glm::vec3& pos, const glm::vec3& vel, float life, const std::string& type) {
    // Find dead particle or overwrite oldest
    bool found = false;
    for (auto& p : m_particles) {
        if (p.life <= 0) {
            p.position = pos;
            p.velocity = vel;
            p.life = life;
            p.maxLife = life;
            p.size = 0.3f;
            p.type = type;
            found = true;
            break;
        }
    }
    
    if (!found && (int)m_particles.size() < m_maxParticles) {
        Particle p;
        p.position = pos;
        p.velocity = vel;
        p.life = life;
        p.maxLife = life;
        p.size = 0.3f;
        p.type = type;
        m_particles.push_back(p);
    }
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 12. ROAD NETWORK
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/game/RoadNetwork.hpp', r'''#pragma once
#include <vector>
#include <string>
#include <glm/glm.hpp>
#include "../renderer/Mesh.hpp"

namespace fc {
class RenderEngine;
class Camera;

struct RoadSegment {
    glm::vec3 start;
    glm::vec3 end;
    float width;
    std::string type; // "highway", "street", "dirt"
};

class RoadNetwork {
public:
    RoadNetwork();
    ~RoadNetwork();
    
    void generateRoads();
    void render(RenderEngine& renderer, const Camera& camera);
    
    std::string getRoadType(float x, float z) const;
    
private:
    std::vector<RoadSegment> m_segments;
    std::vector<Mesh> m_meshes;
    
    void addRoad(const std::vector<glm::vec3>& points, float width, const std::string& type);
    void buildMesh(const RoadSegment& seg);
    std::vector<glm::vec3> smooth(const std::vector<glm::vec3>& points);
};

} // namespace fc
''')

    write_file(BASE_DIR / 'src/game/RoadNetwork.cpp', r'''#include "RoadNetwork.hpp"
#include <cmath>
#include "../renderer/RenderEngine.hpp"
#include "../renderer/Camera.hpp"

namespace fc {

RoadNetwork::RoadNetwork() = default;
RoadNetwork::~RoadNetwork() = default;

void RoadNetwork::generateRoads() {
    // City grid
    const float CR = 350.0f;
    const float BS = 40.0f;
    
    // Avenues
    for (int i = -5; i <= 5; i++) {
        float x = i * BS;
        if (std::abs(x) < CR) {
            std::vector<glm::vec3> pts = {
                {x, 0, -CR},
                {x, 0, CR}
            };
            addRoad(pts, 7.0f, "street");
        }
    }
    
    // Streets
    for (int j = -5; j <= 5; j++) {
        float z = j * BS;
        if (std::abs(z) < CR) {
            std::vector<glm::vec3> pts = {
                {-CR, 0, z},
                {CR, 0, z}
            };
            addRoad(pts, 7.0f, "street");
        }
    }
    
    // Highways
    std::vector<glm::vec3> h1 = {{-CR - 40, 0, 0}, {CR + 40, 0, 0}};
    addRoad(h1, 12.0f, "highway");
    
    std::vector<glm::vec3> h2 = {{0, 0, -CR - 40}, {0, 0, CR + 40}};
    addRoad(h2, 12.0f, "highway");
    
    // Diagonal highways
    std::vector<glm::vec3> d1 = {{-CR, 0, -CR}, {CR, 0, CR}};
    addRoad(d1, 10.0f, "highway");
    
    std::vector<glm::vec3> d2 = {{-CR, 0, CR}, {CR, 0, -CR}};
    addRoad(d2, 10.0f, "highway");
    
    // Ring roads
    for (float r : {CR, CR + 250, CR + 600}) {
        std::vector<glm::vec3> ring;
        for (float a = 0; a < 6.28318f; a += 0.06f) {
            ring.push_back({std::cos(a) * r, 0, std::sin(a) * r});
        }
        addRoad(ring, r >= CR + 300 ? 8.0f : 10.0f, "highway");
    }
    
    // Village connections
    const glm::vec2 villages[] = {
        {-1400, -1000}, {1600, 700}, {-700, 1700}, {1900, -1500}, {-1700, 1300}
    };
    
    for (const auto& v : villages) {
        float a = std::atan2(v.y, v.x);
        float dist = std::sqrt(v.x * v.x + v.y * v.y);
        std::vector<glm::vec3> conn = {
            {std::cos(a) * (CR + 600), 0, std::sin(a) * (CR + 600)},
            {v.x, 0, v.y}
        };
        addRoad(conn, 8.0f, "highway");
    }
    
    // Village-to-village
    for (int i = 0; i < 5; i++) {
        const auto& a = villages[i];
        const auto& b = villages[(i + 1) % 5];
        std::vector<glm::vec3> vv = {{a.x, 0, a.y}, {b.x, 0, b.y}};
        addRoad(vv, 6.0f, "highway");
    }
    
    // Dirt roads
    for (int i = 0; i < 15; i++) {
        float a1 = ((i * 7919) % 10000) / 10000.0f * 6.28318f;
        float d1 = 500 + ((i * 3571) % 10000) / 10000.0f * 800;
        float sx = std::cos(a1) * d1;
        float sz = std::sin(a1) * d1;
        float a2 = a1 + ((i * 2137) % 10000) / 10000.0f * 2 - 1;
        float d2 = 250 + ((i * 4219) % 10000) / 10000.0f * 500;
        
        std::vector<glm::vec3> dirt;
        int n = 20;
        for (int j = 0; j <= n; j++) {
            float t = j / (float)n;
            dirt.push_back({
                sx + (std::cos(a2) * d2 - sx) * t + std::sin(t * 12.9f + sx * 0.01f) * 80,
                0,
                sz + (std::sin(a2) * d2 - sz) * t + std::cos(t * 15.1f + sz * 0.01f) * 80
            });
        }
        addRoad(dirt, 3.0f, "dirt");
    }
}

void RoadNetwork::addRoad(const std::vector<glm::vec3>& points, float width, const std::string& type) {
    auto smoothed = smooth(points);
    for (size_t i = 0; i < smoothed.size() - 1; i++) {
        RoadSegment seg;
        seg.start = smoothed[i];
        seg.end = smoothed[i + 1];
        seg.width = width;
        seg.type = type;
        m_segments.push_back(seg);
        buildMesh(seg);
    }
}

std::vector<glm::vec3> RoadNetwork::smooth(const std::vector<glm::vec3>& points) {
    if (points.size() < 2) return points;
    
    std::vector<glm::vec3> result;
    for (size_t i = 0; i < points.size() - 1; i++) {
        const auto& p0 = points[std::max(0, (int)i - 1)];
        const auto& p1 = points[i];
        const auto& p2 = points[i + 1];
        const auto& p3 = points[std::min(points.size() - 1, i + 2)];
        
        for (int j = 0; j < 8; j++) {
            float t = j / 8.0f;
            float t2 = t * t;
            float t3 = t2 * t;
            
            glm::vec3 pt;
            pt.x = 0.5f * ((2 * p1.x) + (-p0.x + p2.x) * t + (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 + (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3);
            pt.z = 0.5f * ((2 * p1.z) + (-p0.z + p2.z) * t + (2 * p0.z - 5 * p1.z + 4 * p2.z - p3.z) * t2 + (-p0.z + 3 * p1.z - 3 * p2.z + p3.z) * t3);
            pt.y = 0; // Flat for now, terrain will adjust
            result.push_back(pt);
        }
    }
    result.push_back(points.back());
    return result;
}

void RoadNetwork::buildMesh(const RoadSegment& seg) {
    // Build road strip mesh
    std::vector<Vertex> vertices;
    std::vector<unsigned int> indices;
    
    glm::vec3 dir = seg.end - seg.start;
    float len = glm::length(dir);
    if (len < 0.001f) return;
    dir /= len;
    
    glm::vec3 right(-dir.z, 0, dir.x);
    float hw = seg.width / 2.0f;
    
    Vertex v1, v2, v3, v4;
    v1.position = seg.start + right * hw;
    v1.position.y = 0.4f; // Slightly above terrain
    v1.normal = {0, 1, 0};
    v1.texCoord = {0, 0};
    
    v2.position = seg.start - right * hw;
    v2.position.y = 0.4f;
    v2.normal = {0, 1, 0};
    v2.texCoord = {1, 0};
    
    v3.position = seg.end + right * hw;
    v3.position.y = 0.4f;
    v3.normal = {0, 1, 0};
    v3.texCoord = {0, 1};
    
    v4.position = seg.end - right * hw;
    v4.position.y = 0.4f;
    v4.normal = {0, 1, 0};
    v4.texCoord = {1, 1};
    
    // Color based on type
    glm::vec4 color;
    if (seg.type == "highway") color = {0.2f, 0.2f, 0.2f, 1};
    else if (seg.type == "street") color = {0.25f, 0.25f, 0.25f, 1};
    else color = {0.55f, 0.45f, 0.33f, 1}; // Dirt
    
    v1.color = v2.color = v3.color = v4.color = color;
    
    vertices.push_back(v1);
    vertices.push_back(v2);
    vertices.push_back(v3);
    vertices.push_back(v4);
    
    indices.push_back(0);
    indices.push_back(2);
    indices.push_back(1);
    indices.push_back(1);
    indices.push_back(2);
    indices.push_back(3);
    
    Mesh mesh;
    mesh.load(vertices, indices);
    m_meshes.push_back(std::move(mesh));
}

void RoadNetwork::render(RenderEngine& renderer, const Camera& camera) {
    for (auto& mesh : m_meshes) {
        renderer.renderMesh(mesh, glm::mat4(1.0f), renderer.getGeometryShader());
    }
}

std::string RoadNetwork::getRoadType(float x, float z) const {
    float bestDist = 1e9f;
    std::string bestType;
    
    for (const auto& seg : m_segments) {
        // Project point onto segment
        glm::vec3 ab = seg.end - seg.start;
        float len2 = glm::dot(ab, ab);
        if (len2 < 0.001f) continue;
        
        float t = glm::clamp(glm::dot(glm::vec3(x, 0, z) - seg.start, ab) / len2, 0.0f, 1.0f);
        glm::vec3 closest = seg.start + ab * t;
        float dist = std::sqrt((x - closest.x) * (x - closest.x) + (z - closest.z) * (z - closest.z));
        
        if (dist < bestDist && dist < seg.width / 2.0f + 3.0f) {
            bestDist = dist;
            bestType = seg.type;
        }
    }
    
    return bestType;
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 13. BUILDING GENERATOR
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'src/game/BuildingGenerator.hpp', r'''#pragma once
#include <vector>
#include <glm/glm.hpp>
#include "../renderer/Mesh.hpp"

namespace fc {
class RenderEngine;
class Camera;

struct Building {
    glm::vec3 position;
    glm::vec3 size;
    glm::vec4 color;
};

class BuildingGenerator {
public:
    BuildingGenerator();
    ~BuildingGenerator();
    
    void generateBuildings();
    void render(RenderEngine& renderer, const Camera& camera);
    
private:
    std::vector<Building> m_buildings;
    std::vector<Mesh> m_meshes;
    
    void addBuilding(float x, float z, float w, float h, float d);
    bool checkOverlap(float x, float z, float w, float d);
    bool onRoad(float x, float z, float margin);
};

} // namespace fc
''')

    write_file(BASE_DIR / 'src/game/BuildingGenerator.cpp', r'''#include "BuildingGenerator.hpp"
#include <cmath>
#include <cstdlib>
#include "../renderer/RenderEngine.hpp"
#include "../renderer/Camera.hpp"

namespace fc {

BuildingGenerator::BuildingGenerator() = default;
BuildingGenerator::~BuildingGenerator() = default;

void BuildingGenerator::generateBuildings() {
    // City grid buildings
    const float CR = 350.0f;
    const float BS = 40.0f;
    
    for (int ai = -5; ai < 5; ai++) {
        for (int sj = -5; sj < 5; sj++) {
            float x0 = ai * BS + 5;
            float x1 = (ai + 1) * BS - 5;
            float z0 = sj * BS + 5;
            float z1 = (sj + 1) * BS - 5;
            
            if (x1 - x0 < 10 || z1 - z0 < 10) continue;
            
            float mx = (x0 + x1) / 2;
            float mz = (z0 + z1) / 2;
            float distFromCenter = std::sqrt(mx * mx + mz * mz);
            float heightBoost = std::max(0.0f, 1.0f - distFromCenter / CR) * 30.0f;
            
            int nBuildings = 1 + (std::abs(ai * 7 + sj * 13) % 3);
            
            for (int n = 0; n < nBuildings; n++) {
                int s = ai * 100 + sj * 10 + n;
                float bw = 4 + (std::abs(s * 7) % 100) / 100.0f * (x1 - x0 - 10) / nBuildings;
                float bd = 4 + (std::abs(s * 11) % 100) / 100.0f * (z1 - z0 - 10) / nBuildings;
                float bh = 5 + (std::abs(s * 13) % 100) / 100.0f * 15 + heightBoost;
                
                float px = x0 + (std::abs(s * 17) % 100) / 100.0f * (x1 - x0 - bw) + bw / 2;
                float pz = z0 + (std::abs(s * 19) % 100) / 100.0f * (z1 - z0 - bd) + bd / 2;
                
                if (!checkOverlap(px, pz, bw, bd)) {
                    addBuilding(px, pz, bw, bh, bd);
                }
            }
        }
    }
    
    // Village buildings
    const glm::vec2 villages[] = {
        {-1400, -1000}, {1600, 700}, {-700, 1700}, {1900, -1500}, {-1700, 1300}
    };
    
    for (const auto& v : villages) {
        for (int i = 0; i < 12; i++) {
            int s = (int)(v.x * 100 + v.y * 10 + i * 7);
            float a = (std::abs(s * 37) % 360) / 180.0f * 3.14159f;
            float di = 20 + (std::abs(s * 53) % 100) / 100.0f * 120;
            float x = v.x + std::cos(a) * di;
            float z = v.y + std::sin(a) * di;
            float w = 4 + (std::abs(s * 17) % 100) / 100.0f * 7;
            float h = 5 + (std::abs(s * 23) % 100) / 100.0f * 15;
            float d = 4 + (std::abs(s * 29) % 100) / 100.0f * 7;
            
            if (!onRoad(x, z, 2) && !checkOverlap(x, z, w, d)) {
                addBuilding(x, z, w, h, d);
            }
        }
    }
}

void BuildingGenerator::addBuilding(float x, float z, float w, float h, float d) {
    Building b;
    b.position = {x, 0, z};
    b.size = {w, h, d};
    
    // Random color
    int seed = (int)(x * 17 + z * 31);
    float r = 0.25f + (std::abs(seed * 17) % 100) / 100.0f * 0.15f;
    float g = 0.25f + (std::abs(seed * 23) % 100) / 100.0f * 0.15f;
    float bval = 0.3f + (std::abs(seed * 29) % 100) / 100.0f * 0.15f;
    b.color = {r, g, bval, 1};
    
    m_buildings.push_back(b);
    
    // Generate mesh
    Mesh mesh;
    std::vector<Vertex> verts;
    std::vector<unsigned int> idx;
    
    float hw = w / 2, hh = h / 2, hd = d / 2;
    
    // Simple cube
    Vertex v[8];
    v[0].position = {-hw, 0, -hd}; v[0].normal = {-1, 0, -1}; v[0].texCoord = {0, 0};
    v[1].position = {hw, 0, -hd}; v[1].normal = {1, 0, -1}; v[1].texCoord = {1, 0};
    v[2].position = {hw, h, -hd}; v[2].normal = {1, 0, -1}; v[2].texCoord = {1, 1};
    v[3].position = {-hw, h, -hd}; v[3].normal = {-1, 0, -1}; v[3].texCoord = {0, 1};
    v[4].position = {-hw, 0, hd}; v[4].normal = {-1, 0, 1}; v[4].texCoord = {0, 0};
    v[5].position = {hw, 0, hd}; v[5].normal = {1, 0, 1}; v[5].texCoord = {1, 0};
    v[6].position = {hw, h, hd}; v[6].normal = {1, 0, 1}; v[6].texCoord = {1, 1};
    v[7].position = {-hw, h, hd}; v[7].normal = {-1, 0, 1}; v[7].texCoord = {0, 1};
    
    for (int i = 0; i < 8; i++) {
        v[i].position += b.position;
        v[i].color = b.color;
        verts.push_back(v[i]);
    }
    
    // Front, back, top, bottom, left, right
    unsigned int faces[] = {
        0,2,1, 0,3,2, // Front
        4,5,6, 4,6,7, // Back
        3,7,6, 3,6,2, // Top
        0,1,5, 0,5,4, // Bottom
        0,4,7, 0,7,3, // Left
        1,2,6, 1,6,5  // Right
    };
    
    for (int i = 0; i < 36; i++) idx.push_back(faces[i]);
    
    mesh.load(verts, idx);
    m_meshes.push_back(std::move(mesh));
}

bool BuildingGenerator::checkOverlap(float x, float z, float w, float d) {
    for (const auto& b : m_buildings) {
        if (std::abs(x - b.position.x) < (w + b.size.x) / 2 + 1 &&
            std::abs(z - b.position.z) < (d + b.size.z) / 2 + 1) {
            return true;
        }
    }
    return false;
}

bool BuildingGenerator::onRoad(float x, float z, float margin) {
    // Simplified - check distance from known road lines
    // In full implementation, query RoadNetwork
    const float CR = 350.0f;
    const float BS = 40.0f;
    
    // Check grid roads
    for (int i = -5; i <= 5; i++) {
        float rx = i * BS;
        if (std::abs(x - rx) < 3.5f + margin && std::abs(z) < CR) return true;
        float rz = i * BS;
        if (std::abs(z - rz) < 3.5f + margin && std::abs(x) < CR) return true;
    }
    
    return false;
}

void BuildingGenerator::render(RenderEngine& renderer, const Camera& camera) {
    for (auto& mesh : m_meshes) {
        renderer.renderMesh(mesh, glm::mat4(1.0f), renderer.getGeometryShader());
    }
}

} // namespace fc
''')

    # ═══════════════════════════════════════════════════════════════════
    # 14. SHADERS
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'shaders/geometry.vert', r'''#version 460 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec2 aTexCoord;
layout(location = 3) in vec3 aTangent;
layout(location = 4) in vec3 aBitangent;
layout(location = 5) in vec4 aColor;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;
out vec4 Color;
out mat3 TBN;

uniform mat4 model;
uniform mat4 viewProj;

void main() {
    vec4 worldPos = model * vec4(aPos, 1.0);
    FragPos = worldPos.xyz;
    gl_Position = viewProj * worldPos;
    
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoord = aTexCoord;
    Color = aColor;
    
    vec3 T = normalize(mat3(model) * aTangent);
    vec3 B = normalize(mat3(model) * aBitangent);
    vec3 N = normalize(mat3(model) * aNormal);
    TBN = mat3(T, B, N);
}
''')

    write_file(BASE_DIR / 'shaders/geometry.frag', r'''#version 460 core
layout(location = 0) out vec4 gPosition;
layout(location = 1) out vec4 gNormal;
layout(location = 2) out vec4 gAlbedo;
layout(location = 3) out vec4 gMaterial;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;
in vec4 Color;
in mat3 TBN;

uniform vec3 cameraPos;
uniform float metallic;
uniform float roughness;
uniform float ao;

void main() {
    gPosition = vec4(FragPos, 1.0);
    gNormal = vec4(normalize(Normal), 1.0);
    gAlbedo = Color;
    gMaterial = vec4(metallic, roughness, ao, 1.0);
}
''')

    write_file(BASE_DIR / 'shaders/lighting.vert', r'''#version 460 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
    TexCoord = aTexCoord;
}
''')

    write_file(BASE_DIR / 'shaders/lighting.frag', r'''#version 460 core
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D gPosition;
uniform sampler2D gNormal;
uniform sampler2D gAlbedo;
uniform sampler2D gMaterial;

uniform vec3 lightDir;
uniform vec3 lightColor;
uniform float lightIntensity;
uniform vec3 cameraPos;
uniform float exposure;

void main() {
    vec3 fragPos = texture(gPosition, TexCoord).rgb;
    vec3 normal = normalize(texture(gNormal, TexCoord).rgb);
    vec4 albedo = texture(gAlbedo, TexCoord);
    vec4 material = texture(gMaterial, TexCoord);
    
    float metallic = material.r;
    float roughness = material.g;
    float ao = material.b;
    
    // Directional light
    vec3 L = normalize(-lightDir);
    vec3 V = normalize(cameraPos - fragPos);
    vec3 H = normalize(L + V);
    
    float NdotL = max(dot(normal, L), 0.0);
    float NdotV = max(dot(normal, V), 0.0);
    float NdotH = max(dot(normal, H), 0.0);
    
    // Diffuse
    vec3 diffuse = albedo.rgb * NdotL * lightColor * lightIntensity;
    
    // Specular (Blinn-Phong)
    float specPower = mix(8.0, 128.0, 1.0 - roughness);
    float spec = pow(NdotH, specPower) * metallic;
    vec3 specular = vec3(spec) * lightColor * lightIntensity;
    
    // Ambient
    vec3 ambient = albedo.rgb * 0.1 * ao;
    
    vec3 color = ambient + diffuse + specular;
    
    // Tone mapping
    color = color * exposure;
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(1.0 / 2.2));
    
    FragColor = vec4(color, albedo.a);
}
''')

    write_file(BASE_DIR / 'shaders/skybox.vert', r'''#version 460 core
layout(location = 0) in vec3 aPos;

out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view;

void main() {
    TexCoords = aPos;
    vec4 pos = projection * view * vec4(aPos, 1.0);
    gl_Position = pos.xyww;
}
''')

    write_file(BASE_DIR / 'shaders/skybox.frag', r'''#version 460 core
in vec3 TexCoords;

out vec4 FragColor;

uniform vec3 topColor;
uniform vec3 bottomColor;
uniform float offset;
uniform float exponent;

void main() {
    float h = normalize(TexCoords + offset).y;
    float t = max(pow(max(h, 0.0), exponent), 0.0);
    vec3 color = mix(bottomColor, topColor, t);
    FragColor = vec4(color, 1.0);
}
''')

    write_file(BASE_DIR / 'shaders/shadow.vert', r'''#version 460 core
layout(location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 lightSpaceMatrix;

void main() {
    gl_Position = lightSpaceMatrix * model * vec4(aPos, 1.0);
}
''')

    write_file(BASE_DIR / 'shaders/shadow.frag', r'''#version 460 core

void main() {
    // Depth only
}
''')

    write_file(BASE_DIR / 'shaders/particle.vert', r'''#version 460 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aTexCoord;

out vec2 TexCoord;
out float Life;

uniform mat4 viewProj;
uniform vec3 position;
uniform float size;
uniform float life;
uniform float maxLife;

void main() {
    vec3 worldPos = position + aPos * size;
    gl_Position = viewProj * vec4(worldPos, 1.0);
    TexCoord = aTexCoord;
    Life = life / maxLife;
}
''')

    write_file(BASE_DIR / 'shaders/particle.frag', r'''#version 460 core
in vec2 TexCoord;
in float Life;

out vec4 FragColor;

uniform vec3 color;
uniform float opacity;

void main() {
    float dist = length(TexCoord - vec2(0.5));
    float alpha = smoothstep(0.5, 0.0, dist) * opacity * Life;
    FragColor = vec4(color, alpha);
}
''')

    write_file(BASE_DIR / 'shaders/bloom.vert', r'''#version 460 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
    TexCoord = aTexCoord;
}
''')

    write_file(BASE_DIR / 'shaders/bloom.frag', r'''#version 460 core
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D image;
uniform bool horizontal;
uniform float weight[5] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

void main() {
    vec2 texOffset = 1.0 / vec2(textureSize(image, 0));
    vec3 result = texture(image, TexCoord).rgb * weight[0];
    
    if (horizontal) {
        for (int i = 1; i < 5; ++i) {
            result += texture(image, TexCoord + vec2(texOffset.x * i, 0.0)).rgb * weight[i];
            result += texture(image, TexCoord - vec2(texOffset.x * i, 0.0)).rgb * weight[i];
        }
    } else {
        for (int i = 1; i < 5; ++i) {
            result += texture(image, TexCoord + vec2(0.0, texOffset.y * i)).rgb * weight[i];
            result += texture(image, TexCoord - vec2(0.0, texOffset.y * i)).rgb * weight[i];
        }
    }
    
    FragColor = vec4(result, 1.0);
}
''')

    write_file(BASE_DIR / 'shaders/tonemap.vert', r'''#version 460 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
    TexCoord = aTexCoord;
}
''')

    write_file(BASE_DIR / 'shaders/tonemap.frag', r'''#version 460 core
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D scene;
uniform sampler2D bloomBlur;
uniform float exposure;
uniform bool bloom;

void main() {
    vec3 hdrColor = texture(scene, TexCoord).rgb;
    vec3 bloomColor = texture(bloomBlur, TexCoord).rgb;
    if (bloom) hdrColor += bloomColor;
    
    // Reinhard tone mapping
    vec3 mapped = hdrColor * exposure;
    mapped = mapped / (mapped + vec3(1.0));
    
    // Gamma correction
    mapped = pow(mapped, vec3(1.0 / 2.2));
    
    FragColor = vec4(mapped, 1.0);
}
''')

    write_file(BASE_DIR / 'shaders/ssao.vert', r'''#version 460 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
    TexCoord = aTexCoord;
}
''')

    write_file(BASE_DIR / 'shaders/ssao.frag', r'''#version 460 core
in vec2 TexCoord;

out float FragColor;

uniform sampler2D gPosition;
uniform sampler2D gNormal;
uniform sampler2D texNoise;

uniform vec3 samples[64];
uniform mat4 projection;
uniform vec2 noiseScale;

void main() {
    vec3 fragPos = texture(gPosition, TexCoord).xyz;
    vec3 normal = normalize(texture(gNormal, TexCoord).xyz);
    vec3 randomVec = normalize(texture(texNoise, TexCoord * noiseScale).xyz);
    
    vec3 tangent = normalize(randomVec - normal * dot(randomVec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 TBN = mat3(tangent, bitangent, normal);
    
    float occlusion = 0.0;
    float radius = 0.5;
    float bias = 0.025;
    
    for (int i = 0; i < 64; ++i) {
        vec3 samplePos = TBN * samples[i];
        samplePos = fragPos + samplePos * radius;
        
        vec4 offset = vec4(samplePos, 1.0);
        offset = projection * offset;
        offset.xyz = offset.xyz / offset.w * 0.5 + 0.5;
        
        float sampleDepth = texture(gPosition, offset.xy).z;
        float rangeCheck = smoothstep(0.0, 1.0, radius / abs(fragPos.z - sampleDepth));
        occlusion += (sampleDepth >= samplePos.z + bias ? 1.0 : 0.0) * rangeCheck;
    }
    
    FragColor = 1.0 - (occlusion / 64.0);
}
''')

    # ═══════════════════════════════════════════════════════════════════
    # 15. COMPILE SCRIPT
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'compile.sh', r'''#!/bin/bash
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
if command -v pkg-config &> /dev/null; then
    GLFW_CFLAGS=$(pkg-config --cflags glfw3 2>/dev/null || echo "-I/usr/include")
    GLFW_LIBS=$(pkg-config --static --libs glfw3 2>/dev/null || echo "-lglfw -lGL -lX11 -lpthread -lXrandr -lXi -ldl")
else
    GLFW_CFLAGS="-I/usr/include"
    GLFW_LIBS="-lglfw -lGL -lX11 -lpthread -lXrandr -lXi -ldl"
fi

# Compiler flags
CXX=${CXX:-g++}
CXXFLAGS="-std=c++17 -O3 -march=native -ffast-math -Wall -Wextra"
CXXFLAGS="$CXXFLAGS $GLFW_CFLAGS -I./include -I./src"

# Linker flags
LDFLAGS="$GLFW_LIBS -lm"

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
''')
    os.chmod(BASE_DIR / 'compile.sh', 0o755)

    # ═══════════════════════════════════════════════════════════════════
    # 16. CMAKE (alternative build)
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'CMakeLists.txt', r'''cmake_minimum_required(VERSION 3.16)
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
''')

    # ═══════════════════════════════════════════════════════════════════
    # 17. README
    # ═══════════════════════════════════════════════════════════════════
    write_file(BASE_DIR / 'README.md', r'''# FORZA CUBEY WORLD

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
''')

if __name__ == "__main__":
    generate_project()