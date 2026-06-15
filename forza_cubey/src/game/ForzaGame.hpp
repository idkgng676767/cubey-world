#pragma once
#include "IGame.hpp"
#include <memory>
#include <vector>
#include <string>
#include <glm/glm.hpp>
#include "../renderer/Camera.hpp"
#include "../renderer/Mesh.hpp"
#include "../physics/PhysicsEngine.hpp"

namespace fc {

class Terrain;
class Skybox;
class Car;
class ParticleSystem;
class RoadNetwork;
class BuildingGenerator;

struct InputState {
    bool throttle = false;
    bool brake = false;
    bool reverse = false;
    bool left = false;
    bool right = false;
    bool handbrake = false;
    bool reset = false;
    bool lookLeft = false;
    bool lookRight = false;
    bool lookBack = false;
    bool pause = false;
    float mouseX = 0, mouseY = 0;
    bool mouseCaptured = true;
};

class ForzaGame : public IGame {
public:
    ForzaGame();
    ~ForzaGame();
    
    void initialize(GameEngine* engine) override;
    void shutdown() override;
    void processInput(GLFWwindow* window, float dt) override;
    void update(float dt) override;
    void render(RenderEngine* renderer) override;
    void onWindowResize(int width, int height) override;
    
private:
    GameEngine* m_engine = nullptr;
    
    std::unique_ptr<Camera> m_camera;
    std::unique_ptr<Terrain> m_terrain;
    std::unique_ptr<Skybox> m_skybox;
    std::unique_ptr<Car> m_car;
    std::unique_ptr<ParticleSystem> m_particles;
    std::unique_ptr<RoadNetwork> m_roads;
    std::unique_ptr<BuildingGenerator> m_buildings;
    
    InputState m_input;
    PhysicsEngine m_physics;
    
    // Car physics body
    int m_carBodyId = -1;
    int m_carColliderId = -1;
    
    // Camera modes
    enum CamMode { Chase, Hood, Bumper, Drone, Cinematic };
    CamMode m_camMode = Chase;
    float m_camYaw = 0, m_camPitch = 0.3f;
    float m_camDistance = 12.0f;
    float m_camHeight = 3.0f;
    
    // HUD
    struct HUDState {
        float speed = 0;
        float rpm = 0;
        int gear = 1;
        float throttle = 0;
        float brake = 0;
        std::string surface = "OFF-ROAD";
        float lapTime = 0;
        int position = 1;
    } m_hud;
    
    // World
    glm::vec3 m_sunDir{0.3f, -0.8f, 0.5f};
    glm::vec3 m_sunColor{1.0f, 0.95f, 0.8f};
    float m_timeOfDay = 12.0f;
    
    void updateCamera(float dt);
    void updateCarPhysics(float dt);
    void updateHUD(float dt);
    void updateTimeOfDay(float dt);
    void renderHUD();
    
    void setupWorld();
    void setupCar();
    void setupRoads();
    void setupBuildings();
    
    float getTerrainHeight(float x, float z) const;
    glm::vec3 getTerrainNormal(float x, float z) const;
};

} // namespace fc
