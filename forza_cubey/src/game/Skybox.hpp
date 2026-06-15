#pragma once
#include "../renderer/Mesh.hpp"

namespace fc {
class RenderEngine;
class Camera;
class Skybox {
public:
    Skybox();
    ~Skybox();
    void render(RenderEngine& renderer, const Camera& camera) const;
private:
    Mesh m_mesh;
};
} // namespace fc
