#include "RenderEngine.hpp"
#include <glad/glad.h>
#include <iostream>
#include <random>
#include "game/Terrain.hpp"
#include "game/Skybox.hpp"
#include "game/Car.hpp"
#include "game/ParticleSystem.hpp"

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
