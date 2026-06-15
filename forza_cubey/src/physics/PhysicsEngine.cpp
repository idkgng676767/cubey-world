#include "PhysicsEngine.hpp"
#include <algorithm>
#include <cmath>

namespace fc {

void RigidBody::applyForce(const glm::vec3& f) { force += f; }
void RigidBody::applyForceAtPoint(const glm::vec3& f, const glm::vec3& p) {
    force += f;
    torque += glm::cross(p - position, f);
}
void RigidBody::applyTorque(const glm::vec3& t) { torque += t; }
void RigidBody::applyImpulse(const glm::vec3& imp) {
    if (!isKinematic) velocity += imp * invMass;
}
glm::vec3 RigidBody::getForward() const {
    return rotation * glm::vec3(0, 0, -1);
}
glm::vec3 RigidBody::getRight() const {
    return rotation * glm::vec3(1, 0, 0);
}
glm::vec3 RigidBody::getUp() const {
    return rotation * glm::vec3(0, 1, 0);
}

PhysicsEngine::PhysicsEngine() = default;
PhysicsEngine::~PhysicsEngine() = default;

void PhysicsEngine::step(float dt) {
    float subDt = dt / m_substeps;
    for (int s = 0; s < m_substeps; s++) {
        integrate(subDt);
        solveCollisions();
        solveConstraints();
    }
}

void PhysicsEngine::integrate(float dt) {
    for (auto& b : m_bodies) {
        if (b.isKinematic) continue;
        if (b.useGravity) b.force += b.mass * m_gravity;
        b.acceleration = b.force * b.invMass;
        b.velocity += b.acceleration * dt;
        b.velocity *= (1.0f - b.drag * dt);
        b.position += b.velocity * dt;
        b.angularVelocity += b.torque * dt;
        b.angularVelocity *= (1.0f - b.angularDrag * dt);
        glm::quat dq(0, b.angularVelocity.x * 0.5f * dt, b.angularVelocity.y * 0.5f * dt, b.angularVelocity.z * 0.5f * dt);
        b.rotation = glm::normalize(b.rotation + dq * b.rotation);
        b.force = glm::vec3(0);
        b.torque = glm::vec3(0);
    }
}

void PhysicsEngine::solveCollisions() {
    for (size_t i = 0; i < m_bodies.size(); i++) {
        for (size_t j = i + 1; j < m_bodies.size(); j++) {
            for (const auto& ci : m_colliders[i]) {
                for (const auto& cj : m_colliders[j]) {
                    glm::vec3 normal;
                    float depth;
                    bool hit = false;
                    if (ci.type == Collider::Sphere && cj.type == Collider::Sphere)
                        hit = sphereSphere(i, j, normal, depth);
                    else if (ci.type == Collider::Sphere && cj.type == Collider::Box)
                        hit = sphereBox(i, j, normal, depth);
                    else if (ci.type == Collider::Box && cj.type == Collider::Sphere)
                        { hit = sphereBox(j, i, normal, depth); normal = -normal; }
                    else if (ci.type == Collider::Box && cj.type == Collider::Box)
                        hit = boxBox(i, j, normal, depth);
                    if (hit && depth > 0) resolveCollision(i, j, normal, depth);
                }
            }
        }
    }
}

void PhysicsEngine::resolveCollision(int a, int b, const glm::vec3& normal, float depth) {
    auto& ba = m_bodies[a];
    auto& bb = m_bodies[b];
    float totalInvMass = ba.invMass + bb.invMass;
    if (totalInvMass > 0) {
        glm::vec3 corr = normal * depth / totalInvMass;
        if (!ba.isKinematic) ba.position += corr * ba.invMass;
        if (!bb.isKinematic) bb.position -= corr * bb.invMass;
    }
    glm::vec3 relVel = bb.velocity - ba.velocity;
    float velAlong = glm::dot(relVel, normal);
    if (velAlong > 0) return;
    float e = std::min(ba.restitution, bb.restitution);
    float j = -(1 + e) * velAlong / totalInvMass;
    glm::vec3 impulse = j * normal;
    if (!ba.isKinematic) ba.applyImpulse(-impulse);
    if (!bb.isKinematic) bb.applyImpulse(impulse);
    // Friction
    relVel = bb.velocity - ba.velocity;
    glm::vec3 tangent = relVel - normal * velAlong;
    if (glm::length(tangent) > 0.001f) {
        tangent = glm::normalize(tangent);
        float jt = -glm::dot(relVel, tangent) / totalInvMass;
        float mu = std::sqrt(ba.friction * ba.friction + bb.friction * bb.friction);
        glm::vec3 fImpulse = tangent * std::clamp(jt, -mu * j, mu * j);
        if (!ba.isKinematic) ba.applyImpulse(-fImpulse);
        if (!bb.isKinematic) bb.applyImpulse(fImpulse);
    }
}

void PhysicsEngine::solveConstraints() {
    for (auto& b : m_bodies) {
        if (b.position.y < 0 && !b.isKinematic) {
            b.position.y = 0;
            if (b.velocity.y < 0) b.velocity.y *= -b.restitution;
        }
    }
}

int PhysicsEngine::addBody(const RigidBody& body) {
    m_bodies.push_back(body);
    m_colliders.emplace_back();
    return (int)m_bodies.size() - 1;
}

int PhysicsEngine::addCollider(int bodyId, const Collider& col) {
    if (bodyId >= 0 && bodyId < (int)m_colliders.size()) {
        m_colliders[bodyId].push_back(col);
        return (int)m_colliders[bodyId].size() - 1;
    }
    return -1;
}

void PhysicsEngine::setBodyPosition(int id, const glm::vec3& p) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].position = p;
}

void PhysicsEngine::setBodyVelocity(int id, const glm::vec3& v) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].velocity = v;
}

void PhysicsEngine::setBodyRotation(int id, const glm::quat& q) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].rotation = q;
}

void PhysicsEngine::applyForce(int id, const glm::vec3& f) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].applyForce(f);
}

void PhysicsEngine::applyTorque(int id, const glm::vec3& t) {
    if (id >= 0 && id < (int)m_bodies.size()) m_bodies[id].applyTorque(t);
}

RigidBody& PhysicsEngine::getBody(int id) { return m_bodies[id]; }
const RigidBody& PhysicsEngine::getBody(int id) const { return m_bodies[id]; }

RaycastHit PhysicsEngine::raycast(const glm::vec3& origin, const glm::vec3& dir, float maxDist) {
    RaycastHit result;
    result.distance = maxDist;
    for (size_t i = 0; i < m_bodies.size(); i++) {
        for (const auto& col : m_colliders[i]) {
            if (col.type == Collider::Sphere) {
                glm::vec3 oc = origin - (m_bodies[i].position + col.offset);
                float b = glm::dot(oc, dir);
                float c = glm::dot(oc, oc) - col.radius * col.radius;
                float disc = b * b - c;
                if (disc > 0) {
                    float dist = -b - std::sqrt(disc);
                    if (dist > 0 && dist < result.distance) {
                        result.hit = true;
                        result.distance = dist;
                        result.bodyId = (int)i;
                        result.point = origin + dir * dist;
                        result.normal = glm::normalize(result.point - (m_bodies[i].position + col.offset));
                    }
                }
            }
        }
    }
    return result;
}

bool PhysicsEngine::sphereSphere(int a, int b, glm::vec3& normal, float& depth) {
    glm::vec3 diff = (m_bodies[b].position + m_colliders[b][0].offset) - (m_bodies[a].position + m_colliders[a][0].offset);
    float dist = glm::length(diff);
    float minD = m_colliders[a][0].radius + m_colliders[b][0].radius;
    if (dist < minD && dist > 0) {
        normal = -diff / dist;
        depth = minD - dist;
        return true;
    }
    return false;
}

bool PhysicsEngine::sphereBox(int a, int b, glm::vec3& normal, float& depth) {
    glm::vec3 spherePos = m_bodies[a].position + m_colliders[a][0].offset;
    glm::vec3 boxPos = m_bodies[b].position + m_colliders[b][0].offset;
    glm::vec3 closest = glm::clamp(spherePos - boxPos, -m_colliders[b][0].halfExtents, m_colliders[b][0].halfExtents);
    glm::vec3 diff = (spherePos - boxPos) - closest;
    float dist = glm::length(diff);
    if (dist < m_colliders[a][0].radius && dist > 0) {
        normal = -diff / dist;
        depth = m_colliders[a][0].radius - dist;
        return true;
    }
    return false;
}

bool PhysicsEngine::boxBox(int a, int b, glm::vec3& normal, float& depth) {
    glm::vec3 posA = m_bodies[a].position + m_colliders[a][0].offset;
    glm::vec3 posB = m_bodies[b].position + m_colliders[b][0].offset;
    glm::vec3 minA = posA - m_colliders[a][0].halfExtents;
    glm::vec3 maxA = posA + m_colliders[a][0].halfExtents;
    glm::vec3 minB = posB - m_colliders[b][0].halfExtents;
    glm::vec3 maxB = posB + m_colliders[b][0].halfExtents;
    if (maxA.x < minB.x || minA.x > maxB.x) return false;
    if (maxA.y < minB.y || minA.y > maxB.y) return false;
    if (maxA.z < minB.z || minA.z > maxB.z) return false;
    float overlaps[6] = {
        maxA.x - minB.x, maxB.x - minA.x,
        maxA.y - minB.y, maxB.y - minA.y,
        maxA.z - minB.z, maxB.z - minA.z
    };
    float minO = overlaps[0];
    int axis = 0;
    for (int i = 1; i < 6; i++) if (overlaps[i] < minO) { minO = overlaps[i]; axis = i; }
    static const glm::vec3 axes[] = {{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
    normal = axes[axis];
    depth = minO;
    return true;
}

} // namespace fc
