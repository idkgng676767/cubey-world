#include "ParticleSystem.hpp"

namespace fc {

ParticleSystem::ParticleSystem(int maxParticles) : m_maxParticles(maxParticles) {
    m_particles.reserve(maxParticles);
}

ParticleSystem::~ParticleSystem() = default;

void ParticleSystem::update(float dt) {
    for (auto& p : m_particles) {
        if (p.life > 0) {
            p.position += p.velocity * dt;
            p.velocity.y += 0.5f * dt; // Rise
            p.life -= dt;
            p.size += dt * 0.5f; // Grow
        }
    }
}

void ParticleSystem::spawn(const glm::vec3& pos, const glm::vec3& vel, float life, const std::string& type) {
    // Find dead particle or overwrite oldest
    bool found = false;
    for (auto& p : m_particles) {
        if (p.life <= 0) {
            p.position = pos;
            p.velocity = vel;
            p.life = life;
            p.maxLife = life;
            p.size = 0.3f;
            p.type = type;
            found = true;
            break;
        }
    }
    
    if (!found && (int)m_particles.size() < m_maxParticles) {
        Particle p;
        p.position = pos;
        p.velocity = vel;
        p.life = life;
        p.maxLife = life;
        p.size = 0.3f;
        p.type = type;
        m_particles.push_back(p);
    }
}

} // namespace fc
