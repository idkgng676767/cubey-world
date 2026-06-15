#include "Camera.hpp"
#include <cmath>

namespace fc {

Camera::Camera(float fov, float a, float n, float f) : m_fov(fov), m_aspect(a), m_near(n), m_far(f) {
    m_smoothPos = m_pos;
    m_smoothTarget = m_target;
}

void Camera::setPosition(const glm::vec3& p) { m_pos = p; }
void Camera::setTarget(const glm::vec3& t) { m_target = t; }
void Camera::setUp(const glm::vec3& u) { m_up = u; }

void Camera::follow(const glm::vec3& target, float dist, float height, float yaw, float pitch, float lag, float dt) {
    float t = 1.0f - std::exp(-lag * 60.0f * dt);
    m_smoothTarget += (target - m_smoothTarget) * t;

    float cy = std::cos(yaw), sy = std::sin(yaw);
    float cp = std::cos(pitch), sp = std::sin(pitch);

    glm::vec3 desired = m_smoothTarget + glm::vec3(
        sy * cp * dist,
        sp * dist + height,
        cy * cp * dist
    );

    m_smoothPos += (desired - m_smoothPos) * t;
    m_pos = m_smoothPos;
    m_target = m_smoothTarget;
}

glm::mat4 Camera::getView() const {
    return glm::lookAt(m_pos, m_target, m_up);
}

glm::mat4 Camera::getProjection() const {
    return glm::perspective(glm::radians(m_fov), m_aspect, m_near, m_far);
}

glm::vec3 Camera::getForward() const {
    return glm::normalize(m_target - m_pos);
}

glm::vec3 Camera::getRight() const {
    return glm::normalize(glm::cross(getForward(), m_up));
}

void Camera::setFOV(float fov) {
    m_fov = fov;
}

} // namespace fc
