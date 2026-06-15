#pragma once
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>
#include <vector>
#include <memory>
#include "../renderer/Mesh.hpp"

namespace fc {
class RenderEngine;
class Camera;

class Car {
public:
    Car();
    ~Car();
    
    void setPosition(const glm::vec3& pos);
    void setRotation(const glm::quat& rot);
    
    void render(RenderEngine& renderer, const Camera& camera) const;
    
    glm::vec3 getPosition() const { return m_position; }
    glm::quat getRotation() const { return m_rotation; }
    
private:
    glm::vec3 m_position{0, 0, 0};
    glm::quat m_rotation{1, 0, 0, 0};
    
    // Car parts
    Mesh m_chassis;
    Mesh m_cabin;
    Mesh m_wheel;
    Mesh m_spoiler;
    
    void generateCar();
};

} // namespace fc
