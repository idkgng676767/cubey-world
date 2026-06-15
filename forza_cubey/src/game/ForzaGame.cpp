#include "ForzaGame.hpp"
#include <glad/glad.h>
#include <iostream>
#include <cmath>
#include <cstdlib>
#include <GLFW/glfw3.h>
#include "../engine/GameEngine.hpp"
#include "../renderer/RenderEngine.hpp"
#include "Terrain.hpp"
#include "Skybox.hpp"
#include "Car.hpp"
#include "ParticleSystem.hpp"
#include "RoadNetwork.hpp"
#include "BuildingGenerator.hpp"

namespace fc {

ForzaGame::ForzaGame() = default;
ForzaGame::~ForzaGame() = default;

void ForzaGame::initialize(GameEngine* engine) {
    m_engine = engine;
    std::cout << "[Game] Initializing Forza Cubey World...\n";
    
    int w, h;
    glfwGetWindowSize(engine->getWindow(), &w, &h);
    
    m_camera = std::make_unique<Camera>(70.0f, (float)w/h, 0.1f, 5000.0f);
    
    setupWorld();
    setupCar();
    setupRoads();
    setupBuildings();
    
    m_skybox = std::make_unique<Skybox>();
    m_particles = std::make_unique<ParticleSystem>(10000);
    
    m_physics.setGravity(glm::vec3(0, -15.0f, 0));
    
    std::cout << "[Game] Initialization complete!\n";
}

void ForzaGame::shutdown() {
    std::cout << "[Game] Shutting down...\n";
}

void ForzaGame::processInput(GLFWwindow* window, float dt) {
    m_input.throttle = glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS || 
                       glfwGetKey(window, GLFW_KEY_UP) == GLFW_PRESS;
    m_input.brake = glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS;
    m_input.reverse = glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS ||
                      glfwGetKey(window, GLFW_KEY_DOWN) == GLFW_PRESS;
    m_input.left = glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS ||
                   glfwGetKey(window, GLFW_KEY_LEFT) == GLFW_PRESS;
    m_input.right = glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS ||
                    glfwGetKey(window, GLFW_KEY_RIGHT) == GLFW_PRESS;
    m_input.handbrake = glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS;
    m_input.reset = glfwGetKey(window, GLFW_KEY_R) == GLFW_PRESS;
    m_input.lookLeft = glfwGetKey(window, GLFW_KEY_Q) == GLFW_PRESS;
    m_input.lookRight = glfwGetKey(window, GLFW_KEY_E) == GLFW_PRESS;
    m_input.lookBack = glfwGetKey(window, GLFW_KEY_C) == GLFW_PRESS;
    m_input.pause = glfwGetKey(window, GLFW_KEY_P) == GLFW_PRESS;
    
    if (glfwGetKey(window, GLFW_KEY_1) == GLFW_PRESS) m_camMode = Chase;
    if (glfwGetKey(window, GLFW_KEY_2) == GLFW_PRESS) m_camMode = Hood;
    if (glfwGetKey(window, GLFW_KEY_3) == GLFW_PRESS) m_camMode = Bumper;
    if (glfwGetKey(window, GLFW_KEY_4) == GLFW_PRESS) m_camMode = Drone;
    if (glfwGetKey(window, GLFW_KEY_5) == GLFW_PRESS) m_camMode = Cinematic;
    
    // Mouse look (only in chase/drone mode)
    if (m_camMode == Chase || m_camMode == Drone) {
        if (m_input.mouseCaptured) {
            double mx, my;
            glfwGetCursorPos(window, &mx, &my);
            float dx = (float)(mx - m_input.mouseX) * 0.005f;
            float dy = (float)(my - m_input.mouseY) * 0.005f;
            m_camYaw -= dx;
            m_camPitch += dy;
            m_camPitch = glm::clamp(m_camPitch, -1.5f, 1.5f);
            m_input.mouseX = mx;
            m_input.mouseY = my;
        }
    }
    
    if (m_input.reset) {
        auto& body = m_physics.getBody(m_carBodyId);
        body.position = glm::vec3(0, getTerrainHeight(0, 0) + 1.0f, 0);
        body.velocity = glm::vec3(0);
        body.rotation = glm::quat(1, 0, 0, 0);
        body.angularVelocity = glm::vec3(0);
    }
}

void ForzaGame::update(float dt) {
    updateCarPhysics(dt);
    updateCamera(dt);
    updateHUD(dt);
    updateTimeOfDay(dt);
    
    m_physics.step(dt);
    m_particles->update(dt);
    
    // Update car visual from physics
    if (m_carBodyId >= 0) {
        auto& body = m_physics.getBody(m_carBodyId);
        m_car->setPosition(body.position);
        m_car->setRotation(body.rotation);
    }
}

void ForzaGame::render(RenderEngine* renderer) {
    renderer->setCamera(*m_camera);  // <-- ADD THIS
    // Set lighting
    DirectionalLight light;
    light.direction = m_sunDir;
    light.color = m_sunColor;
    light.intensity = 2.5f;
    renderer->setLight(light);
    
    // Skybox
    renderer->renderSkybox(*m_skybox, *m_camera);
    
    // Terrain
    renderer->renderTerrain(*m_terrain, *m_camera);
    
    // Roads
    m_roads->render(*renderer, *m_camera);
    
    // Buildings
    m_buildings->render(*renderer, *m_camera);
    
    // Car
    renderer->renderCar(*m_car, *m_camera);
    
    // Particles
    renderer->renderParticles(m_particles->getParticles());
    
    // HUD
    renderHUD();
}

void ForzaGame::onWindowResize(int width, int height) {
    // Handle resize
}

void ForzaGame::setupWorld() {
    m_terrain = std::make_unique<Terrain>(5000.0f, 250);
    m_terrain->init(); 
}

void ForzaGame::setupCar() {
    m_car = std::make_unique<Car>();
    
    // Create physics body
    RigidBody body;
    body.position = glm::vec3(0, getTerrainHeight(0, 0) + 1.0f, 0);
    body.mass = 1200.0f;
    body.invMass = 1.0f / body.mass;
    body.restitution = 0.2f;
    body.friction = 0.8f;
    body.drag = 0.02f;
    body.angularDrag = 0.1f;
    
    m_carBodyId = m_physics.addBody(body);
    
    // Car collider (box)
    Collider collider;
    collider.type = Collider::Box;
    collider.halfExtents = glm::vec3(1.0f, 0.5f, 2.2f);
    collider.offset = glm::vec3(0, 0.5f, 0);
    m_carColliderId = m_physics.addCollider(m_carBodyId, collider);
    
    // Wheel colliders
    Collider wheelCol;
    wheelCol.type = Collider::Sphere;
    wheelCol.radius = 0.35f;
    wheelCol.offset = glm::vec3(-1.05f, 0.35f, -1.3f);
    m_physics.addCollider(m_carBodyId, wheelCol);
    wheelCol.offset = glm::vec3(1.05f, 0.35f, -1.3f);
    m_physics.addCollider(m_carBodyId, wheelCol);
    wheelCol.offset = glm::vec3(-1.05f, 0.35f, 1.3f);
    m_physics.addCollider(m_carBodyId, wheelCol);
    wheelCol.offset = glm::vec3(1.05f, 0.35f, 1.3f);
    m_physics.addCollider(m_carBodyId, wheelCol);
}

void ForzaGame::setupRoads() {
    m_roads = std::make_unique<RoadNetwork>();
    m_roads->generateRoads();
}

void ForzaGame::setupBuildings() {
    m_buildings = std::make_unique<BuildingGenerator>();
    m_buildings->generateBuildings();
}

void ForzaGame::updateCamera(float dt) {
    if (!m_car) return;
    
    auto& body = m_physics.getBody(m_carBodyId);
    glm::vec3 carPos = body.position;
    glm::vec3 carForward = body.getForward();
    
    float targetDist = m_camDistance;
    float targetHeight = m_camHeight;
    float lag = 3.0f;
    
    switch (m_camMode) {
        case Chase:
            targetDist = 12.0f;
            targetHeight = 3.0f;
            break;
        case Hood:
            targetDist = 0.5f;
            targetHeight = 1.2f;
            lag = 15.0f;
            m_camYaw = 0;
            m_camPitch = 0;
            break;
        case Bumper:
            targetDist = -2.5f;
            targetHeight = 0.8f;
            lag = 15.0f;
            m_camYaw = 0;
            m_camPitch = 0;
            break;
        case Drone:
            targetDist = 30.0f;
            targetHeight = 20.0f;
            lag = 1.0f;
            break;
        case Cinematic:
            targetDist = 8.0f;
            targetHeight = 2.0f;
            lag = 5.0f;
            // Auto-rotate
            m_camYaw += dt * 0.2f;
            break;
    }
    
    // Speed-based FOV
    float speed = glm::length(body.velocity) * 3.6f; // km/h
    float targetFOV = 70.0f + glm::clamp(speed / 200.0f, 0.0f, 1.0f) * 20.0f;
    float currentFOV = m_camera->getFOV();
    m_camera->setFOV(currentFOV + (targetFOV - currentFOV) * dt * 5.0f);
    
    // Camera shake at high speed
    glm::vec3 shake(0);
    if (speed > 150.0f) {
        float shakeAmount = (speed - 150.0f) / 150.0f * 0.03f;
        shake.x = (rand() / (float)RAND_MAX - 0.5f) * shakeAmount;
        shake.y = (rand() / (float)RAND_MAX - 0.5f) * shakeAmount;
    }
    
    m_camera->follow(carPos, targetDist, targetHeight, m_camYaw, m_camPitch, lag, dt);
    
    // Add shake
    if (speed > 150.0f) {
        auto pos = m_camera->getPosition();
        m_camera->setPosition(pos + shake);
    }
}

void ForzaGame::updateCarPhysics(float dt) {
    if (m_carBodyId < 0) return;
    
    auto& body = m_physics.getBody(m_carBodyId);
    
    // Get road type at current position
    std::string roadType = m_roads->getRoadType(body.position.x, body.position.z);
    
    // Physics params based on surface
    float maxSpeed = 90.0f; // m/s ~= 324 km/h
    float accel = 30.0f;
    float brakeForce = 60.0f;
    float friction = 0.8f;
    float turnSpeed = 2.5f;
    
    if (roadType == "highway") {
        maxSpeed = 90.0f;
        friction = 0.9f;
    } else if (roadType == "street") {
        maxSpeed = 72.0f;
        friction = 0.85f;
    } else if (roadType == "dirt") {
        maxSpeed = 40.0f;
        friction = 0.5f;
        accel = 20.0f;
        turnSpeed = 1.5f;
    } else {
        // Off-road
        maxSpeed = 50.0f;
        friction = 0.4f;
        accel = 15.0f;
        turnSpeed = 1.2f;
    }
    
    // Apply handbrake
    if (m_input.handbrake) {
        friction *= 0.3f;
        // Drift physics
    }
    
    // Throttle
    if (m_input.throttle) {
        glm::vec3 forward = body.getForward();
        float currentSpeed = glm::dot(body.velocity, forward);
        if (currentSpeed < maxSpeed) {
            body.applyForce(forward * accel * body.mass);
        }
    }
    
    // Brake/Reverse
    if (m_input.brake) {
        glm::vec3 forward = body.getForward();
        float currentSpeed = glm::dot(body.velocity, forward);
        if (currentSpeed > 0.5f) {
            // Braking
            body.applyForce(-forward * brakeForce * body.mass);
        } else {
            // Reverse
            body.applyForce(-forward * accel * 0.5f * body.mass);
        }
    }
    
    // Steering
    if (m_input.left || m_input.right) {
        float steer = m_input.left ? 1.0f : -1.0f;
        float speed = glm::length(body.velocity);
        float steerFactor = glm::clamp(speed / 20.0f, 0.0f, 1.0f);
        
        // Apply steering torque
        glm::vec3 up = body.getUp();
        body.applyTorque(up * steer * turnSpeed * steerFactor * body.mass);
        
        // Counter-steer at low speed
        if (speed < 5.0f) {
            glm::vec3 forward = body.getForward();
            body.applyForce(forward * steer * 5.0f * body.mass);
        }
    }
    
    // Apply surface friction
    glm::vec3 vel = body.velocity;
    glm::vec3 forward = body.getForward();
    glm::vec3 right = body.getRight();
    
    float fwdSpeed = glm::dot(vel, forward);
    float rightSpeed = glm::dot(vel, right);
    
    // Lateral friction (prevents sliding)
    body.applyForce(-right * rightSpeed * friction * body.mass * 5.0f);
    
    // Rolling resistance
    body.applyForce(-forward * fwdSpeed * 0.01f * body.mass);
    
    // Air resistance
    float airDrag = 0.001f * fwdSpeed * fwdSpeed;
    body.applyForce(-forward * airDrag * body.mass);
    
    // Gravity on slopes
    float terrainH = getTerrainHeight(body.position.x, body.position.z);
    float terrainHFront = getTerrainHeight(
        body.position.x + forward.x * 2.0f, 
        body.position.z + forward.z * 2.0f
    );
    float slope = (terrainHFront - terrainH) / 2.0f;
    body.applyForce(glm::vec3(0, -slope * 9.81f * body.mass, 0));
    
    // Keep car on terrain
    body.position.y = terrainH + 0.6f;
    
    // Particle effects
    float speed = glm::length(body.velocity);
    if (m_input.brake && speed > 15.0f) {
        // Tire smoke
        for (int i = 0; i < 2; i++) {
            glm::vec3 wheelPos = body.position + body.rotation * glm::vec3(
                i == 0 ? -1.05f : 1.05f, 0.1f, 1.3f
            );
            m_particles->spawn(wheelPos, glm::vec3(0, 1, 0), 0.5f, "smoke");
        }
    }
    
    if (roadType.empty() && speed > 5.0f) {
        // Dust off-road
        for (int i = 0; i < 2; i++) {
            glm::vec3 wheelPos = body.position + body.rotation * glm::vec3(
                (i == 0 ? -1.0f : 1.0f) * (rand() / (float)RAND_MAX), 
                0, 
                (rand() / (float)RAND_MAX - 0.5f) * 2.0f
            );
            m_particles->spawn(wheelPos, glm::vec3(0, 0.5f, 0), 0.6f, "dust");
        }
    }
    
    if (m_input.throttle && speed > 1.0f) {
        // Exhaust
        glm::vec3 exhaustPos = body.position + body.rotation * glm::vec3(0.55f, 0.3f, 2.2f);
        glm::vec3 exhaustVel = -forward * 2.0f + glm::vec3(0, 1, 0);
        m_particles->spawn(exhaustPos, exhaustVel, 0.5f, "smoke");
    }
}

void ForzaGame::updateHUD(float dt) {
    if (m_carBodyId < 0) return;
    
    auto& body = m_physics.getBody(m_carBodyId);
    float speed = glm::length(body.velocity) * 3.6f; // km/h
    
    m_hud.speed = speed;
    m_hud.throttle = m_input.throttle ? 1.0f : 0.0f;
    m_hud.brake = m_input.brake ? 1.0f : 0.0f;
    
    // Calculate gear and RPM
    float absSpeed = std::abs(speed);
    if (absSpeed < 0.5f) {
        m_hud.gear = 0; // Neutral
        m_hud.rpm = 850.0f + std::sin(glfwGetTime() * 5.0f) * 40.0f;
    } else if (speed < 0) {
        m_hud.gear = -1; // Reverse
        m_hud.rpm = 1500.0f + absSpeed / 25.0f * 3500.0f;
    } else {
        // Forward gears
        const float gearLimits[] = {0, 35, 65, 100, 140, 190, 250, 300};
        m_hud.gear = 1;
        for (int i = 1; i < 7; i++) {
            if (absSpeed > gearLimits[i]) m_hud.gear = i;
        }
        
        float prev = gearLimits[m_hud.gear - 1];
        float next = gearLimits[m_hud.gear];
        float ratio = (absSpeed - prev) / std::max(1.0f, next - prev);
        m_hud.rpm = 1500.0f + ratio * 5000.0f + m_hud.gear * 150.0f;
        m_hud.rpm = std::min(8000.0f, std::max(800.0f, m_hud.rpm));
    }
    
    m_hud.surface = m_roads->getRoadType(body.position.x, body.position.z);
    if (m_hud.surface.empty()) m_hud.surface = "OFF-ROAD";
    
    m_hud.lapTime += dt;
}

void ForzaGame::updateTimeOfDay(float dt) {
    // Optional: cycle time of day
    // m_timeOfDay += dt * 0.1f;
    // if (m_timeOfDay >= 24.0f) m_timeOfDay -= 24.0f;
    
    // Update sun direction based on time
    float angle = (m_timeOfDay - 6.0f) / 12.0f * 3.14159f; // 6am to 6pm
    m_sunDir.x = std::cos(angle) * 0.5f;
    m_sunDir.y = -std::sin(angle);
    m_sunDir.z = 0.3f;
    m_sunDir = glm::normalize(m_sunDir);
}

void ForzaGame::renderHUD() {
    // HUD rendering is done via ImGui or direct OpenGL
    // For now, this is a placeholder - integrate with your UI system
}

float ForzaGame::getTerrainHeight(float x, float z) const {
    if (m_terrain) return m_terrain->getHeight(x, z);
    return 0.0f;
}

glm::vec3 ForzaGame::getTerrainNormal(float x, float z) const {
    if (m_terrain) return m_terrain->getNormal(x, z);
    return glm::vec3(0, 1, 0);
}

} // namespace fc
