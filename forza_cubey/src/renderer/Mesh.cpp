#include "Mesh.hpp"
#include <cmath>

namespace fc {

Mesh::Mesh() = default;
Mesh::~Mesh() {
    if (m_vao) glDeleteVertexArrays(1, &m_vao);
    if (m_vbo) glDeleteBuffers(1, &m_vbo);
    if (m_ebo) glDeleteBuffers(1, &m_ebo);
}

void Mesh::setupBuffers(const std::vector<Vertex>& verts, const std::vector<unsigned int>& idx) {
    m_indexCount = idx.size();
    glGenVertexArrays(1, &m_vao);
    glGenBuffers(1, &m_vbo);
    glGenBuffers(1, &m_ebo);

    glBindVertexArray(m_vao);
    glBindBuffer(GL_ARRAY_BUFFER, m_vbo);
    glBufferData(GL_ARRAY_BUFFER, verts.size() * sizeof(Vertex), verts.data(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, m_ebo);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx.size() * sizeof(unsigned int), idx.data(), GL_STATIC_DRAW);

    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)0);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, normal));
    glEnableVertexAttribArray(2);
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, texCoord));
    glEnableVertexAttribArray(3);
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, tangent));
    glEnableVertexAttribArray(4);
    glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, bitangent));
    glEnableVertexAttribArray(5);
    glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, color));

    glBindVertexArray(0);
}

void Mesh::load(const std::vector<Vertex>& verts, const std::vector<unsigned int>& idx) {
    setupBuffers(verts, idx);
}

void Mesh::generatePlane(float w, float d, int subs) {
    std::vector<Vertex> verts;
    std::vector<unsigned int> idx;
    float dx = w / subs, dz = d / subs;
    float du = 1.0f / subs, dv = 1.0f / subs;

    for (int z = 0; z <= subs; z++) {
        for (int x = 0; x <= subs; x++) {
            Vertex v;
            v.position = {x * dx - w/2, 0, z * dz - d/2};
            v.normal = {0, 1, 0};
            v.texCoord = {x * du, z * dv};
            v.tangent = {1, 0, 0};
            v.bitangent = {0, 0, 1};
            verts.push_back(v);
        }
    }
    for (int z = 0; z < subs; z++) {
        for (int x = 0; x < subs; x++) {
            int i0 = z * (subs + 1) + x;
            int i1 = i0 + 1;
            int i2 = i0 + (subs + 1);
            int i3 = i2 + 1;
            idx.push_back(i0); idx.push_back(i2); idx.push_back(i1);
            idx.push_back(i1); idx.push_back(i2); idx.push_back(i3);
        }
    }
    setupBuffers(verts, idx);
}

void Mesh::generateCube(float s) {
    float h = s / 2;
    std::vector<Vertex> verts = {
        // Front
        {{-h,-h,h},{0,0,1},{0,0},{1,0,0},{0,1,0},{1,1,1,1}},
        {{ h,-h,h},{0,0,1},{1,0},{1,0,0},{0,1,0},{1,1,1,1}},
        {{ h, h,h},{0,0,1},{1,1},{1,0,0},{0,1,0},{1,1,1,1}},
        {{-h, h,h},{0,0,1},{0,1},{1,0,0},{0,1,0},{1,1,1,1}},
        // Back
        {{ h,-h,-h},{0,0,-1},{0,0},{-1,0,0},{0,1,0},{1,1,1,1}},
        {{-h,-h,-h},{0,0,-1},{1,0},{-1,0,0},{0,1,0},{1,1,1,1}},
        {{-h, h,-h},{0,0,-1},{1,1},{-1,0,0},{0,1,0},{1,1,1,1}},
        {{ h, h,-h},{0,0,-1},{0,1},{-1,0,0},{0,1,0},{1,1,1,1}},
        // Top
        {{-h,h,h},{0,1,0},{0,0},{1,0,0},{0,0,-1},{1,1,1,1}},
        {{ h,h,h},{0,1,0},{1,0},{1,0,0},{0,0,-1},{1,1,1,1}},
        {{ h,h,-h},{0,1,0},{1,1},{1,0,0},{0,0,-1},{1,1,1,1}},
        {{-h,h,-h},{0,1,0},{0,1},{1,0,0},{0,0,-1},{1,1,1,1}},
        // Bottom
        {{-h,-h,-h},{0,-1,0},{0,0},{1,0,0},{0,0,1},{1,1,1,1}},
        {{ h,-h,-h},{0,-1,0},{1,0},{1,0,0},{0,0,1},{1,1,1,1}},
        {{ h,-h,h},{0,-1,0},{1,1},{1,0,0},{0,0,1},{1,1,1,1}},
        {{-h,-h,h},{0,-1,0},{0,1},{1,0,0},{0,0,1},{1,1,1,1}},
        // Right
        {{ h,-h,h},{1,0,0},{0,0},{0,0,1},{0,1,0},{1,1,1,1}},
        {{ h,-h,-h},{1,0,0},{1,0},{0,0,1},{0,1,0},{1,1,1,1}},
        {{ h, h,-h},{1,0,0},{1,1},{0,0,1},{0,1,0},{1,1,1,1}},
        {{ h, h,h},{1,0,0},{0,1},{0,0,1},{0,1,0},{1,1,1,1}},
        // Left
        {{-h,-h,-h},{-1,0,0},{0,0},{0,0,-1},{0,1,0},{1,1,1,1}},
        {{-h,-h,h},{-1,0,0},{1,0},{0,0,-1},{0,1,0},{1,1,1,1}},
        {{-h, h,h},{-1,0,0},{1,1},{0,0,-1},{0,1,0},{1,1,1,1}},
        {{-h, h,-h},{-1,0,0},{0,1},{0,0,-1},{0,1,0},{1,1,1,1}},
    };
    std::vector<unsigned int> idx = {
        0,1,2,0,2,3, 4,5,6,4,6,7, 8,9,10,8,10,11,
        12,13,14,12,14,15, 16,17,18,16,18,19, 20,21,22,20,22,23
    };
    setupBuffers(verts, idx);
}

void Mesh::generateSphere(float r, int segs) {
    std::vector<Vertex> verts;
    std::vector<unsigned int> idx;
    for (int y = 0; y <= segs; y++) {
        float v = (float)y / segs;
        float phi = v * 3.14159f;
        for (int x = 0; x <= segs; x++) {
            float u = (float)x / segs;
            float theta = u * 2 * 3.14159f;
            float sp = std::sin(phi), cp = std::cos(phi);
            float st = std::sin(theta), ct = std::cos(theta);
            Vertex vrt;
            vrt.position = {r * sp * ct, r * cp, r * sp * st};
            vrt.normal = glm::normalize(vrt.position);
            vrt.texCoord = {u, v};
            vrt.tangent = {-st, 0, ct};
            vrt.bitangent = glm::cross(vrt.normal, vrt.tangent);
            verts.push_back(vrt);
        }
    }
    for (int y = 0; y < segs; y++) {
        for (int x = 0; x < segs; x++) {
            int i0 = y * (segs + 1) + x;
            int i1 = i0 + 1;
            int i2 = i0 + (segs + 1);
            int i3 = i2 + 1;
            if (y != 0) { idx.push_back(i0); idx.push_back(i2); idx.push_back(i1); }
            if (y != segs - 1) { idx.push_back(i1); idx.push_back(i2); idx.push_back(i3); }
        }
    }
    setupBuffers(verts, idx);
}

void Mesh::generateCylinder(float rad, float h, int segs) {
    std::vector<Vertex> verts;
    std::vector<unsigned int> idx;
    float h2 = h / 2;

    // Top center
    Vertex tc; tc.position = {0, h2, 0}; tc.normal = {0, 1, 0}; tc.texCoord = {0.5f, 0.5f};
    verts.push_back(tc);
    // Bottom center
    Vertex bc; bc.position = {0, -h2, 0}; bc.normal = {0, -1, 0}; bc.texCoord = {0.5f, 0.5f};
    verts.push_back(bc);

    for (int i = 0; i <= segs; i++) {
        float a = (float)i / segs * 2 * 3.14159f;
        float c = std::cos(a), s = std::sin(a);

        Vertex v1; v1.position = {rad * c, h2, rad * s}; v1.normal = {0, 1, 0};
        v1.texCoord = {c * 0.5f + 0.5f, s * 0.5f + 0.5f};
        verts.push_back(v1);

        Vertex v2; v2.position = {rad * c, -h2, rad * s}; v2.normal = {0, -1, 0};
        v2.texCoord = {c * 0.5f + 0.5f, s * 0.5f + 0.5f};
        verts.push_back(v2);

        Vertex v3; v3.position = {rad * c, h2, rad * s}; v3.normal = {c, 0, s};
        v3.texCoord = {(float)i / segs, 1}; v3.tangent = {-s, 0, c};
        verts.push_back(v3);

        Vertex v4; v4.position = {rad * c, -h2, rad * s}; v4.normal = {c, 0, s};
        v4.texCoord = {(float)i / segs, 0}; v4.tangent = {-s, 0, c};
        verts.push_back(v4);
    }

    int rs = 2, ss = rs + (segs + 1) * 2;
    for (int i = 0; i < segs; i++) {
        idx.push_back(0); idx.push_back(rs + i * 2); idx.push_back(rs + ((i + 1) % segs) * 2);
        idx.push_back(1); idx.push_back(rs + ((i + 1) % segs) * 2 + 1); idx.push_back(rs + i * 2 + 1);
        int i0 = ss + i * 2, i1 = ss + ((i + 1) % segs) * 2;
        int i2 = ss + i * 2 + 1, i3 = ss + ((i + 1) % segs) * 2 + 1;
        idx.push_back(i0); idx.push_back(i1); idx.push_back(i2);
        idx.push_back(i2); idx.push_back(i1); idx.push_back(i3);
    }
    setupBuffers(verts, idx);
}

void Mesh::generateTorus(float majorR, float minorR, int majorSegs, int minorSegs) {
    std::vector<Vertex> verts;
    std::vector<unsigned int> idx;
    for (int i = 0; i <= majorSegs; i++) {
        float u = (float)i / majorSegs * 2 * 3.14159f;
        for (int j = 0; j <= minorSegs; j++) {
            float v = (float)j / minorSegs * 2 * 3.14159f;
            Vertex vt;
            vt.position = {
                (majorR + minorR * std::cos(v)) * std::cos(u),
                minorR * std::sin(v),
                (majorR + minorR * std::cos(v)) * std::sin(u)
            };
            float du = -std::sin(u), dv = std::cos(u);
            vt.normal = {std::cos(v) * std::cos(u), std::sin(v), std::cos(v) * std::sin(u)};
            vt.texCoord = {(float)i / majorSegs, (float)j / minorSegs};
            vt.tangent = {du, 0, dv};
            vt.bitangent = glm::cross(vt.normal, vt.tangent);
            verts.push_back(vt);
        }
    }
    for (int i = 0; i < majorSegs; i++) {
        for (int j = 0; j < minorSegs; j++) {
            int i0 = i * (minorSegs + 1) + j;
            int i1 = i0 + 1;
            int i2 = i0 + (minorSegs + 1);
            int i3 = i2 + 1;
            idx.push_back(i0); idx.push_back(i2); idx.push_back(i1);
            idx.push_back(i1); idx.push_back(i2); idx.push_back(i3);
        }
    }
    setupBuffers(verts, idx);
}

void Mesh::bind() const { glBindVertexArray(m_vao); }
void Mesh::unbind() const { glBindVertexArray(0); }

} // namespace fc
