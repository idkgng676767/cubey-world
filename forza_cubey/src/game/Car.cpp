#include "Car.hpp"
#include "../renderer/RenderEngine.hpp"
#include "../renderer/Camera.hpp"

namespace fc {

Car::Car() {
    generateCar();
}

Car::~Car() = default;

void Car::generateCar() {
    // Chassis
    m_chassis.generateCube(1.0f);
    // Cabin
    m_cabin.generateCube(0.8f);
    // Wheel
    m_wheel.generateCylinder(0.35f, 0.25f, 16);
    // Spoiler
    m_spoiler.generateCube(0.3f);
}

void Car::setPosition(const glm::vec3& pos) {
    m_position = pos;
}

void Car::setRotation(const glm::quat& rot) {
    m_rotation = rot;
}

void Car::render(RenderEngine& renderer, const Camera& camera) const {
    glm::mat4 model = glm::translate(glm::mat4(1.0f), m_position);
    model *= glm::mat4_cast(m_rotation);
    
    // Render chassis
    glm::mat4 chassisMat = model;
    chassisMat = glm::scale(chassisMat, glm::vec3(2.0f, 0.65f, 4.2f));
    chassisMat = glm::translate(chassisMat, glm::vec3(0, 0.6f, 0));
    // renderer.renderMesh(m_chassis, chassisMat, carPaintShader);
    
    // Render cabin
    glm::mat4 cabinMat = model;
    cabinMat = glm::scale(cabinMat, glm::vec3(1.7f, 0.55f, 2.0f));
    cabinMat = glm::translate(cabinMat, glm::vec3(0, 1.2f, 0.3f));
    // renderer.renderMesh(m_cabin, cabinMat, glassShader);
    
    // Render wheels
    float wheelPositions[4][3] = {
        {-1.05f, 0.35f, -1.3f},
        {1.05f, 0.35f, -1.3f},
        {-1.05f, 0.35f, 1.3f},
        {1.05f, 0.35f, 1.3f}
    };
    
    for (int i = 0; i < 4; i++) {
        glm::mat4 wheelMat = model;
        wheelMat = glm::translate(wheelMat, glm::vec3(wheelPositions[i][0], wheelPositions[i][1], wheelPositions[i][2]));
        wheelMat = glm::rotate(wheelMat, glm::radians(90.0f), glm::vec3(0, 0, 1));
        // renderer.renderMesh(m_wheel, wheelMat, tireShader);
    }
    
    // Render spoiler
    glm::mat4 spoilerMat = model;
    spoilerMat = glm::scale(spoilerMat, glm::vec3(2.2f, 0.06f, 0.35f));
    spoilerMat = glm::translate(spoilerMat, glm::vec3(0, 1.12f, 1.85f));
    // renderer.renderMesh(m_spoiler, spoilerMat, carPaintShader);
}

} // namespace fc
