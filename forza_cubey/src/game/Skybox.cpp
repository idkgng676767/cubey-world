#include "Skybox.hpp"
#include "../renderer/RenderEngine.hpp"
#include "../renderer/Camera.hpp"

namespace fc {

Skybox::Skybox() {
    m_mesh.generateSphere(1.0f, 32);
}

Skybox::~Skybox() = default;

void Skybox::render(RenderEngine& renderer, const Camera& camera) const {
    // Render skybox with special shader (no depth write)
    glm::mat4 model = glm::mat4(1.0f);
    // renderer.renderSkyboxMesh(m_mesh, model);
}

} // namespace fc
