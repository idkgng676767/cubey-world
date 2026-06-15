#pragma once
#include <vector>
#include <glm/glm.hpp>
#include "../renderer/Mesh.hpp"

namespace fc {

class RenderEngine;
class Camera;

class Terrain {
public:
    Terrain(float size, int segments);
    void init();
    ~Terrain();
    
    void render(RenderEngine& renderer, const Camera& camera) const;
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
