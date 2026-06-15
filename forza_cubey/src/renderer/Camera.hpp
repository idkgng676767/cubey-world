#pragma once
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

namespace fc {
class Camera {
public:
    Camera(float fov, float aspect, float near, float far);
    void setPosition(const glm::vec3& p);
    void setTarget(const glm::vec3& t);
    void setUp(const glm::vec3& u);
    void follow(const glm::vec3& target, float dist, float height, float yaw, float pitch, float lag, float dt);
    glm::mat4 getView() const;
    glm::mat4 getProjection() const;
    glm::vec3 getPosition() const { return m_pos; }
    glm::vec3 getForward() const;
    glm::vec3 getRight() const;
    void setFOV(float fov);
    float getFOV() const { return m_fov; }
private:
    glm::vec3 m_pos{0,5,10}, m_target{0,0,0}, m_up{0,1,0};
    float m_fov, m_aspect, m_near, m_far;
    glm::vec3 m_smoothPos, m_smoothTarget;
};
} // namespace fc
