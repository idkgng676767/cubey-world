#pragma once
#include <vector>
#include <glm/glm.hpp>
#include <string>

namespace fc {

struct Particle {
    glm::vec3 position;
    glm::vec3 velocity;
    float life;
    float maxLife;
    float size;
    std::string type;
};

class ParticleSystem {
public:
    ParticleSystem(int maxParticles);
    ~ParticleSystem();
    
    void update(float dt);
    void spawn(const glm::vec3& pos, const glm::vec3& vel, float life, const std::string& type);
    
    const std::vector<Particle>& getParticles() const { return m_particles; }
    
private:
    int m_maxParticles;
    std::vector<Particle> m_particles;
    int m_nextIndex = 0;
};

} // namespace fc
