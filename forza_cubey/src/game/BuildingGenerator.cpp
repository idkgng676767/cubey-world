#include "BuildingGenerator.hpp"
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
