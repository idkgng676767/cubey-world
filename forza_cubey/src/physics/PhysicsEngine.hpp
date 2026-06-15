#pragma once
#include <vector>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

namespace fc {

struct RigidBody {
    glm::vec3 position{0,0,0};
    glm::vec3 velocity{0,0,0};
    glm::vec3 acceleration{0,0,0};
    glm::quat rotation{1,0,0,0};
    glm::vec3 angularVelocity{0,0,0};
    float mass = 1.0f, invMass = 1.0f;
    float restitution = 0.3f, friction = 0.5f;
    float drag = 0.01f, angularDrag = 0.05f;
    bool isKinematic = false, useGravity = true;
    glm::vec3 force{0,0,0}, torque{0,0,0};
    void applyForce(const glm::vec3& f);
    void applyForceAtPoint(const glm::vec3& f, const glm::vec3& p);
    void applyTorque(const glm::vec3& t);
    void applyImpulse(const glm::vec3& imp);
    glm::vec3 getForward() const;
    glm::vec3 getRight() const;
    glm::vec3 getUp() const;
};

struct Collider {
    enum Type { Sphere, Box, Capsule, Mesh } type;
    glm::vec3 offset{0,0,0};
    glm::vec3 halfExtents{1,1,1};
    float radius = 1.0f;
};

struct RaycastHit {
    int bodyId = -1;
    glm::vec3 point, normal;
    float distance = 0;
    bool hit = false;
};

class PhysicsEngine {
public:
    PhysicsEngine();
    ~PhysicsEngine();
    void step(float dt);
    void setGravity(const glm::vec3& g) { m_gravity = g; }
    int addBody(const RigidBody& body);
    int addCollider(int bodyId, const Collider& col);
    void setBodyPosition(int id, const glm::vec3& p);
    void setBodyVelocity(int id, const glm::vec3& v);
    void setBodyRotation(int id, const glm::quat& q);
    void applyForce(int id, const glm::vec3& f);
    void applyTorque(int id, const glm::vec3& t);
    RigidBody& getBody(int id);
    const RigidBody& getBody(int id) const;
    RaycastHit raycast(const glm::vec3& origin, const glm::vec3& dir, float maxDist);
    void setSubsteps(int s) { m_substeps = s; }
    int getBodyCount() const { return (int)m_bodies.size(); }
private:
    std::vector<RigidBody> m_bodies;
    std::vector<std::vector<Collider>> m_colliders;
    glm::vec3 m_gravity{0, -9.81f, 0};
    int m_substeps = 4;
    void integrate(float dt);
    void solveCollisions();
    void solveConstraints();
    bool sphereSphere(int a, int b, glm::vec3& normal, float& depth);
    bool sphereBox(int a, int b, glm::vec3& normal, float& depth);
    bool boxBox(int a, int b, glm::vec3& normal, float& depth);
    void resolveCollision(int a, int b, const glm::vec3& normal, float depth);
};

} // namespace fc
