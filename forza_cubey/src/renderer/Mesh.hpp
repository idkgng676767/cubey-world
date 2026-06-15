#pragma once
#include <vector>
#include <glm/glm.hpp>
#include <glad/glad.h>

namespace fc {

struct Vertex {
    glm::vec3 position;
    glm::vec3 normal;
    glm::vec2 texCoord;
    glm::vec3 tangent;
    glm::vec3 bitangent;
    glm::vec4 color{1,1,1,1};
};

struct Material {
    glm::vec3 albedo{1,1,1};
    float metallic = 0.0f, roughness = 0.5f, ao = 1.0f;
    GLuint albedoMap = 0, normalMap = 0, metallicMap = 0, roughnessMap = 0, aoMap = 0;
};

class Mesh {
public:
    Mesh();
    ~Mesh();
    void load(const std::vector<Vertex>& verts, const std::vector<unsigned int>& idx);
    void generatePlane(float w, float d, int subs);
    void generateCube(float s);
    void generateSphere(float r, int segs);
    void generateCylinder(float r, float h, int segs);
    void generateTorus(float majorR, float minorR, int majorSegs, int minorSegs);
    void bind() const;
    void unbind() const;
    unsigned int getIndexCount() const { return m_indexCount; }
    void setMaterial(const Material* m) { m_material = m; }
    const Material* getMaterial() const { return m_material; }
private:
    GLuint m_vao = 0, m_vbo = 0, m_ebo = 0;
    unsigned int m_indexCount = 0;
    const Material* m_material = nullptr;
    void setupBuffers(const std::vector<Vertex>& verts, const std::vector<unsigned int>& idx);
};

} // namespace fc
