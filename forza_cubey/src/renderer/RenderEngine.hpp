#pragma once
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
