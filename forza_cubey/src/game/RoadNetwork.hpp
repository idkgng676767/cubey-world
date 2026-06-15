#pragma once
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
