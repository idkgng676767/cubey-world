#pragma once
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
