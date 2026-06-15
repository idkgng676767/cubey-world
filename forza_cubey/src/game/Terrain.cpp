#include "Terrain.hpp"
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

void Terrain::render(RenderEngine& renderer, const Camera& camera) const {
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
