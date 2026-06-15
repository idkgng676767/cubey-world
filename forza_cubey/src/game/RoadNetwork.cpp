#include "RoadNetwork.hpp"
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
